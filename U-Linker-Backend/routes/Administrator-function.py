"""
管理员功能路由
功能：
1. 学号精准索引用户全景记录（新增）
2. 查看所有用户信息
3. 管理用户积分（支持争议撤销）
4. 惩罚/解封用户
5. 系统统计
6. 导出帖子为 Excel
7. 从 Excel 导入帖子
"""
from flask import Blueprint, request, session, send_file
from extensions import db
from models import User, Post, PointsHistory, Order, Application
from utils.response import success, error
from sqlalchemy import or_, and_, desc
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ================= 权限检查装饰器 =================
def admin_required(f):
    """管理员权限检查装饰器 [cite: 106]"""
    def wrapper(*args, **kwargs):
        current_user_id = session.get('user_id')
        if not current_user_id:
            return error(message="请先登录")

        current_user = db.session.get(User, current_user_id)
        # 严格限制仅限管理员访问
        if not current_user or not current_user.is_admin:
            return error(message="权限不足：需要管理员权限")

        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ================= 1. 【新增】根据学号获取用户全景记录 =================
@admin_bp.route('/users/by_student_id/<string:sid>', methods=['GET'])
@admin_required
def get_user_by_student_id(sid):
    """
    根据学号索引用户，并返回其"我需要"、"我能提供"帖子及积分明细。
    对应你描述的：输入学号 -> 点击确认 -> 呈现相应内容流程。
    """
    # 精准匹配学号 [cite: 215, 368]
    # 先尝试精确匹配
    user = User.query.filter_by(student_id=sid).first()

    # 如果精确匹配失败，尝试字符串匹配（处理可能的空格或类型问题）
    if not user:
        user = User.query.filter(User.student_id == str(sid).strip()).first()

    # 如果还是找不到，尝试模糊匹配（用于调试）
    if not user:
        # 调试：查看数据库中是否有类似的学号
        similar_users = User.query.filter(User.student_id.like(f'%{sid}%')).all()
        if similar_users:
            similar_ids = [u.student_id for u in similar_users]
            return error(message=f"未找到学号 '{sid}' 对应的用户。相似的学号有：{', '.join(similar_ids)}")

    if not user:
        return error(message=f"未找到学号 '{sid}' 对应的用户。请确认学号是否正确。")

    # 获取该用户发布的“我需要”帖子 (Bounty)
    i_need = Post.query.filter_by(author_id=user.id, post_type='bounty').order_by(desc(Post.created_at)).all()

    # 获取该用户发布的“我能提供”帖子 (Service)
    i_provide = Post.query.filter_by(author_id=user.id, post_type='service').order_by(desc(Post.created_at)).all()

    # 获取该用户的积分明细报表
    history = PointsHistory.query.filter_by(user_id=user.id).order_by(desc(PointsHistory.created_at)).all()

    return success(data={
        'user_info': user.to_dict(),
        'posts': {
            'i_need': [p.to_dict() for p in i_need],      # 对应前端“我需要”选项
            'i_provide': [p.to_dict() for p in i_provide] # 对应前端“我提供”选项
        },
        'points_history': [h.to_dict() for h in history]  # 对应积分记录，支持颜色规范
    })

# ================= 2. 获取所有用户列表 (支持模糊搜索) =================
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '')
    query = User.query
    if keyword:
        keyword_pattern = f'%{keyword}%'
        query = query.filter(
            or_(
                User.username.like(keyword_pattern),
                User.name.like(keyword_pattern),
                User.student_id.like(keyword_pattern),
                User.college.like(keyword_pattern)
            )
        )

    query = query.order_by(desc(User.id))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        'total': pagination.total,
        'items': [user.to_dict() for user in pagination.items]
    })

# ================= 3. 管理用户积分 (支持争议撤销) =================
@admin_bp.route('/users/<int:user_id>/points', methods=['POST'])
@admin_required
def manage_user_points(user_id):
    """
    管理员修改积分。
    注意：根据 SRS 5.1.6.6，管理员仲裁时允许余额变为负数（债务）。 [cite: 335, 336]
    """
    data = request.get_json()
    points_change = data.get('points_change') # 变化量
    reason = data.get('reason', '管理员调整')
    
    if points_change is None:
        return error(message="请提供积分变化量")
    
    user = db.session.get(User, user_id)
    if not user:
        return error(message="用户不存在")
    
    try:
        # 记录旧值用于反馈
        old_points = user.points
        # 执行积分变动（此处不拦截负数，以支持债务记录）
        user.points += int(points_change)
        
        # 必须记录在积分报表中
        history = PointsHistory(
            user_id=user_id,
            points_change=points_change,
            action='管理员仲裁',
            description=reason
        )
        db.session.add(history)
        db.session.commit()
        
        return success(message="积分操作成功", data={
            'new_points': user.points,
            'points_change': points_change
        })
    except Exception as e:
        db.session.rollback()
        return error(message=f"操作失败: {str(e)}")

# ================= 4. 惩罚用户（封禁） =================
@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@admin_required
def ban_user(user_id):
    data = request.get_json()
    reason = data.get('reason', '恶意行为')
    ban_days = data.get('ban_days', 3)
    
    user = db.session.get(User, user_id)
    if not user or user.is_admin:
        return error(message="无法操作该用户")
    
    user.ban_count = (user.ban_count or 0) + 1
    # 阶梯式封禁逻辑
    ban_duration = ban_days * user.ban_count
    user.ban_until = datetime.now() + timedelta(days=ban_duration)
    db.session.commit()
    
    # 返回封禁信息，供前端显示
    return success(
        message=f"已封禁 {ban_duration} 天",
        data={
            'ban_duration_days': ban_duration,
            'ban_until': user.ban_until.strftime('%Y-%m-%d %H:%M:%S') if user.ban_until else None,
            'ban_count': user.ban_count,
            'reason': reason
        }
    )

# ================= 4.1 解封用户 =================
@admin_bp.route('/users/<int:user_id>/unban', methods=['POST'])
@admin_required
def unban_user(user_id):
    """解封用户"""
    user = db.session.get(User, user_id)
    if not user:
        return error(message="用户不存在")
    
    if not user.ban_until:
        return error(message="该用户未被封禁")
    
    # 检查是否已经过期
    if user.ban_until < datetime.now():
        return error(message="该用户的封禁已过期，无需解封")
    
    # 解封：清除封禁时间（保留封禁次数，用于下次封禁时计算）
    user.ban_until = None
    
    db.session.commit()
    
    return success(
        message="用户已解封",
        data={
            'ban_until': None,
            'ban_count': user.ban_count
        }
    )

# ================= 5. 系统统计信息 =================
@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """
    获取全站统计数据
    注意：这里的"active"是指"可用用户"（没有被封禁或封禁已过期的用户）
    与统计接口中的"active_users_last_7_days"（最近7天有操作的用户）是不同的概念
    """
    return success(data={
        'users': {
            'total': User.query.count(),
            'active': User.query.filter(or_(User.ban_until.is_(None), User.ban_until < datetime.now())).count(),  # 可用用户：没有被封禁或封禁已过期
            'banned': User.query.filter(User.ban_until.isnot(None)).filter(User.ban_until >= datetime.now()).count()
        },
        'posts': {
            'total': Post.query.count()
        },
        'orders': {
            'total': Order.query.count()
        },
        'points_circulating': db.session.query(db.func.sum(User.points)).scalar() or 0
    })

# ================= 5.1 获取所有订单列表 =================
@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """获取所有订单列表（管理员）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 20, type=int)
    status = request.args.get('status', '')  # 可选的状态筛选
    
    # 构建查询
    query = Order.query
    
    # 状态筛选
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(desc(Order.created_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 构建返回数据
    items = []
    for order in pagination.items:
        order_dict = order.to_dict()
        items.append(order_dict)
    
    return success(data={
        'total': pagination.total,
        'items': items
    })

# ================= 5.2 获取所有积分流动记录 =================
@admin_bp.route('/points/history', methods=['GET'])
@admin_required
def get_all_points_history():
    """获取所有积分流动记录（管理员）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 20, type=int)
    
    # 构建查询
    query = PointsHistory.query.join(User, PointsHistory.user_id == User.id)
    
    query = query.order_by(desc(PointsHistory.created_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 构建返回数据
    items = []
    for history in pagination.items:
        history_dict = history.to_dict()
        # 添加用户信息
        if history.user:
            history_dict['user_info'] = {
                'id': history.user.id,
                'name': history.user.name,
                'username': history.user.username,
                'college': history.user.college
            }
        items.append(history_dict)
    
    return success(data={
        'total': pagination.total,
        'items': items
    })

# ================= 5.3 获取所有帖子列表 =================
@admin_bp.route('/posts', methods=['GET'])
@admin_required
def get_all_posts():
    """获取所有帖子列表（管理员）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 20, type=int)
    keyword = request.args.get('keyword', '')
    
    # 构建查询
    query = Post.query.join(User, Post.author_id == User.id)
    
    # 关键词搜索（标题、内容、作者名）
    if keyword:
        keyword_pattern = f'%{keyword}%'
        query = query.filter(
            or_(
                Post.title.like(keyword_pattern),
                Post.content.like(keyword_pattern),
                User.name.like(keyword_pattern),
                User.username.like(keyword_pattern)
            )
        )
    
    query = query.order_by(desc(Post.created_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 构建返回数据
    items = []
    for post in pagination.items:
        post_dict = post.to_dict()
        # 添加作者信息
        if post.author:
            post_dict['author'] = {
                'id': post.author.id,
                'name': post.author.name,
                'username': post.author.username,
                'college': post.author.college
            }
        items.append(post_dict)
    
    return success(data={
        'total': pagination.total,
        'items': items
    })
# ================= 5.4 统计接口：每日新增用户和发帖量 =================
@admin_bp.route('/stats/daily', methods=['GET'])
@admin_required
def get_daily_stats():
    """
    获取每日新增用户和发帖量统计
    支持参数:start_date, end_date, group_by
    """
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        group_by = request.args.get('group_by', 'day')  # day, week, month
        
        # 设置默认时间范围（最近30天）
        if not end_date_str:
            # 默认结束日期为今天，设置为23:59:59确保包含今天的所有数据
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            try:
                # 解析日期并设置为当天的23:59:59，确保包含当天的所有数据
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                return error(message="结束日期格式错误,请使用YYYY-MM-DD格式")
        
        if not start_date_str:
            # 默认开始日期为30天前，设置为00:00:00确保包含当天的所有数据
            start_date = (end_date - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            try:
                # 解析日期并设置为当天的00:00:00，确保包含当天的所有数据
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                return error(message="开始日期格式错误,请使用YYYY-MM-DD格式")
        
        # 确保开始日期不晚于结束日期
        if start_date > end_date:
            return error(message="开始日期不能晚于结束日期")
        
        # 根据分组方式调整查询
        date_format_map = {
            'day': '%Y-%m-%d',
            'week': '%Y-%U',  # 年份-周数
            'month': '%Y-%m'
        }
        
        date_format = date_format_map.get(group_by, '%Y-%m-%d')
        
        # 查询每日新增用户统计
        if group_by == 'day':
            # 按天统计
            user_stats_query = db.session.query(
                db.func.date(User.created_at).label('date'),
                db.func.count(User.id).label('new_users')
            ).filter(
                User.created_at >= start_date,
                User.created_at <= end_date
            ).group_by(
                db.func.date(User.created_at)
            ).order_by(
                db.func.date(User.created_at)
            ).all()
        else:
            # 按周/月统计
            user_stats_query = db.session.query(
                db.func.strftime(date_format, User.created_at).label('period'),
                db.func.count(User.id).label('new_users')
            ).filter(
                User.created_at >= start_date,
                User.created_at <= end_date
            ).group_by(
                db.func.strftime(date_format, User.created_at)
            ).order_by(
                db.func.strftime(date_format, User.created_at)
            ).all()
        
        # 查询每日新增帖子统计
        if group_by == 'day':
            post_stats_query = db.session.query(
                db.func.date(Post.created_at).label('date'),
                db.func.count(Post.id).label('new_posts'),
                Post.post_type
            ).filter(
                Post.created_at >= start_date,
                Post.created_at <= end_date
            ).group_by(
                db.func.date(Post.created_at),
                Post.post_type
            ).order_by(
                db.func.date(Post.created_at)
            ).all()
        else:
            post_stats_query = db.session.query(
                db.func.strftime(date_format, Post.created_at).label('period'),
                db.func.count(Post.id).label('new_posts'),
                Post.post_type
            ).filter(
                Post.created_at >= start_date,
                Post.created_at <= end_date
            ).group_by(
                db.func.strftime(date_format, Post.created_at),
                Post.post_type
            ).order_by(
                db.func.strftime(date_format, Post.created_at)
            ).all()
        
        # 查询活跃用户数（最近7天有登录或注册的用户）
        # 注意：这里的"活跃用户"是指最近7天有操作的用户，与get_stats()中的"active"（可用用户）不同
        # - get_stats()中的"active"：没有被封禁或封禁已过期的用户（可用用户）
        # - 这里的"active_users"：最近7天有登录或注册的用户（活跃用户）
        seven_days_ago = datetime.now() - timedelta(days=7)
        active_users_last_7_days = User.query.filter(
            or_(
                User.last_login >= seven_days_ago,
                User.created_at >= seven_days_ago
            )
        ).count()
        
        # 组织数据
        stats_data = []
        
        if group_by == 'day':
            # 按天组织数据
            date_range = []
            current_date = start_date.date()
            end_date_date = end_date.date()
            
            while current_date <= end_date_date:
                date_range.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
            
            # 构建按天统计的数据结构
            date_stats_map = {}
            for date_str in date_range:
                date_stats_map[date_str] = {
                    'date': date_str,
                    'new_users': 0,
                    'new_posts_total': 0,
                    'new_bounties': 0,  # 悬赏任务
                    'new_services': 0,  # 服务任务
                }
            
            # 填充用户数据
            for stat in user_stats_query:
                # 处理日期格式：可能是datetime、date对象或字符串
                if isinstance(stat.date, datetime):
                    date_str = stat.date.strftime('%Y-%m-%d')
                elif hasattr(stat.date, 'strftime'):
                    # date对象
                    date_str = stat.date.strftime('%Y-%m-%d')
                else:
                    # 字符串或其他格式
                    date_str = str(stat.date)
                    # 如果是datetime字符串，尝试解析
                    try:
                        if ' ' in date_str or 'T' in date_str:
                            date_str = datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                
                if date_str in date_stats_map:
                    date_stats_map[date_str]['new_users'] = stat.new_users
            
            # 填充帖子数据
            for stat in post_stats_query:
                # 处理日期格式
                if isinstance(stat.date, datetime):
                    date_str = stat.date.strftime('%Y-%m-%d')
                elif hasattr(stat.date, 'strftime'):
                    # date对象
                    date_str = stat.date.strftime('%Y-%m-%d')
                else:
                    # 字符串或其他格式
                    date_str = str(stat.date)
                    # 如果是datetime字符串，尝试解析
                    try:
                        if ' ' in date_str or 'T' in date_str:
                            date_str = datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                
                if date_str in date_stats_map:
                    date_stats_map[date_str]['new_posts_total'] += stat.new_posts
                    if stat.post_type == 'bounty':
                        date_stats_map[date_str]['new_bounties'] += stat.new_posts  # 累加而不是覆盖
                    elif stat.post_type == 'service':
                        date_stats_map[date_str]['new_services'] += stat.new_posts  # 累加而不是覆盖
            
            # 转换为列表
            for date_str in date_range:
                if date_str in date_stats_map:
                    stats_data.append(date_stats_map[date_str])
        else:
            # 按周/月组织数据
            period_stats_map = {}
            
            # 填充用户数据
            for stat in user_stats_query:
                period = stat.period
                period_stats_map[period] = {
                    'period': period,
                    'new_users': stat.new_users,
                    'new_posts_total': 0,
                    'new_bounties': 0,
                    'new_services': 0
                }
            
            # 填充帖子数据
            for stat in post_stats_query:
                period = stat.period
                if period not in period_stats_map:
                    period_stats_map[period] = {
                        'period': period,
                        'new_users': 0,
                        'new_posts_total': 0,
                        'new_bounties': 0,
                        'new_services': 0
                    }
                
                period_stats_map[period]['new_posts_total'] += stat.new_posts
                if stat.post_type == 'bounty':
                    period_stats_map[period]['new_bounties'] += stat.new_posts
                elif stat.post_type == 'service':
                    period_stats_map[period]['new_services'] += stat.new_posts
            
            # 转换为列表并按期间排序
            stats_data = list(period_stats_map.values())
            stats_data.sort(key=lambda x: x['period'])
        
        # 计算总数
        total_new_users = sum(item['new_users'] for item in stats_data)
        total_new_posts = sum(item['new_posts_total'] for item in stats_data)
        total_new_bounties = sum(item.get('new_bounties', 0) for item in stats_data)
        total_new_services = sum(item.get('new_services', 0) for item in stats_data)
        
        return success(data={
            'time_range': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'group_by': group_by
            },
            'summary': {
                'total_new_users': total_new_users,
                'total_new_posts': total_new_posts,
                'total_new_bounties': total_new_bounties,
                'total_new_services': total_new_services,
                'active_users_last_7_days': active_users_last_7_days  # 最近7天有操作的用户
            },
            'daily_stats': stats_data
        })
        
    except Exception as e:
        return error(message=f"获取统计数据失败: {str(e)}")


# ================= 5.5 导出统计数据为Excel =================
@admin_bp.route('/stats/export', methods=['GET'])
@admin_required
def export_stats_excel():
    """
    导出统计数据为Excel文件
    参数:start_date, end_date, group_by, data_types (可选:users,posts,all)
    """
    try:
        # 获取查询参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        group_by = request.args.get('group_by', 'day')
        data_types = request.args.get('data_types', 'all')  # users, posts, all
        
        # 设置默认时间范围 - 与get_daily_stats保持一致
        if not end_date_str:
            # 默认结束日期为今天，设置为23:59:59确保包含今天的所有数据
            end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            try:
                # 解析日期并设置为当天的23:59:59，确保包含当天的所有数据
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                return error(message="结束日期格式错误,请使用YYYY-MM-DD格式")
        
        if not start_date_str:
            # 默认开始日期为30天前，设置为00:00:00确保包含当天的所有数据
            start_date = (end_date - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            try:
                # 解析日期并设置为当天的00:00:00，确保包含当天的所有数据
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                return error(message="开始日期格式错误,请使用YYYY-MM-DD格式")
        
        # 检查日期范围
        if start_date > end_date:
            return error(message="开始日期不能晚于结束日期")
        
        # 获取统计数据 
        # 复制 get_daily_stats 的查询逻辑
        date_format_map = {
            'day': '%Y-%m-%d',
            'week': '%Y-%U',
            'month': '%Y-%m'
        }
        date_format = date_format_map.get(group_by, '%Y-%m-%d')
        
        # 查询用户统计
        if group_by == 'day':
            user_stats_query = db.session.query(
                db.func.date(User.created_at).label('date'),
                db.func.count(User.id).label('new_users')
            ).filter(
                User.created_at >= start_date,
                User.created_at <= end_date
            ).group_by(
                db.func.date(User.created_at)
            ).all()
        else:
            user_stats_query = db.session.query(
                db.func.strftime(date_format, User.created_at).label('period'),
                db.func.count(User.id).label('new_users')
            ).filter(
                User.created_at >= start_date,
                User.created_at <= end_date
            ).group_by(
                db.func.strftime(date_format, User.created_at)
            ).all()
        
        # 查询帖子统计
        if group_by == 'day':
            post_stats_query = db.session.query(
                db.func.date(Post.created_at).label('date'),
                db.func.count(Post.id).label('new_posts'),
                Post.post_type
            ).filter(
                Post.created_at >= start_date,
                Post.created_at <= end_date
            ).group_by(
                db.func.date(Post.created_at),
                Post.post_type
            ).all()
        else:
            post_stats_query = db.session.query(
                db.func.strftime(date_format, Post.created_at).label('period'),
                db.func.count(Post.id).label('new_posts'),
                Post.post_type
            ).filter(
                Post.created_at >= start_date,
                Post.created_at <= end_date
            ).group_by(
                db.func.strftime(date_format, Post.created_at),
                Post.post_type
            ).all()
        
        # 计算统计数据
        stats_data = []
        if group_by == 'day':
            # 按天组织数据
            date_range = []
            current_date = start_date.date()
            end_date_date = end_date.date()
            
            while current_date <= end_date_date:
                date_range.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
            
            date_stats_map = {}
            for date_str in date_range:
                date_stats_map[date_str] = {
                    'date': date_str,
                    'new_users': 0,
                    'new_posts_total': 0,
                    'new_bounties': 0,
                    'new_services': 0,
                }
            
            # 填充用户数据
            for stat in user_stats_query:
                # 处理日期格式：可能是datetime、date对象或字符串
                if isinstance(stat.date, datetime):
                    date_str = stat.date.strftime('%Y-%m-%d')
                elif hasattr(stat.date, 'strftime'):
                    # date对象
                    date_str = stat.date.strftime('%Y-%m-%d')
                else:
                    # 字符串或其他格式
                    date_str = str(stat.date)
                    # 如果是datetime字符串，尝试解析
                    try:
                        if ' ' in date_str or 'T' in date_str:
                            date_str = datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                
                if date_str in date_stats_map:
                    date_stats_map[date_str]['new_users'] = stat.new_users
            
            # 填充帖子数据
            for stat in post_stats_query:
                # 处理日期格式：可能是datetime、date对象或字符串
                if isinstance(stat.date, datetime):
                    date_str = stat.date.strftime('%Y-%m-%d')
                elif hasattr(stat.date, 'strftime'):
                    # date对象
                    date_str = stat.date.strftime('%Y-%m-%d')
                else:
                    # 字符串或其他格式
                    date_str = str(stat.date)
                    # 如果是datetime字符串，尝试解析
                    try:
                        if ' ' in date_str or 'T' in date_str:
                            date_str = datetime.strptime(date_str.split()[0], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                
                if date_str in date_stats_map:
                    date_stats_map[date_str]['new_posts_total'] += stat.new_posts
                    if stat.post_type == 'bounty':
                        date_stats_map[date_str]['new_bounties'] += stat.new_posts  # 累加而不是覆盖
                    elif stat.post_type == 'service':
                        date_stats_map[date_str]['new_services'] += stat.new_posts  # 累加而不是覆盖
            
            for date_str in date_range:
                if date_str in date_stats_map:
                    stats_data.append(date_stats_map[date_str])
        else:
            # 按周/月组织数据
            period_stats_map = {}
            
            for stat in user_stats_query:
                period = stat.period
                period_stats_map[period] = {
                    'period': period,
                    'new_users': stat.new_users,
                    'new_posts_total': 0,
                    'new_bounties': 0,
                    'new_services': 0
                }
            
            for stat in post_stats_query:
                period = stat.period
                if period not in period_stats_map:
                    period_stats_map[period] = {
                        'period': period,
                        'new_users': 0,
                        'new_posts_total': 0,
                        'new_bounties': 0,
                        'new_services': 0
                    }
                
                period_stats_map[period]['new_posts_total'] += stat.new_posts
                if stat.post_type == 'bounty':
                    period_stats_map[period]['new_bounties'] += stat.new_posts
                elif stat.post_type == 'service':
                    period_stats_map[period]['new_services'] += stat.new_posts
            
            stats_data = list(period_stats_map.values())
            stats_data.sort(key=lambda x: x['period'])
        
        # 计算总数
        total_new_users = sum(item['new_users'] for item in stats_data)
        total_new_posts = sum(item['new_posts_total'] for item in stats_data)
        total_new_bounties = sum(item.get('new_bounties', 0) for item in stats_data)
        total_new_services = sum(item.get('new_services', 0) for item in stats_data)
        
        # 查询活跃用户数（最近7天有登录或注册的用户）
        # 注意：这里的"活跃用户"是指最近7天有操作的用户，与get_stats()中的"active"（可用用户）不同
        seven_days_ago = datetime.now() - timedelta(days=7)
        active_users_last_7_days = User.query.filter(
            or_(
                User.last_login >= seven_days_ago,
                User.created_at >= seven_days_ago
            )
        ).count()
        
        # 创建Excel写入器
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 1. 统计摘要工作表
            summary_data = {
                '统计项目': [
                    '统计时间范围',
                    '开始日期',
                    '结束日期',
                    '分组方式',
                    '新增用户总数',
                    '新增帖子总数',
                    '新增悬赏任务数',
                    '新增服务任务数',
                    '最近7天活跃用户数'
                ],
                '数值': [
                    f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d'),
                    '按天' if group_by == 'day' else '按周' if group_by == 'week' else '按月',
                    total_new_users,
                    total_new_posts,
                    total_new_bounties,
                    total_new_services,
                    active_users_last_7_days
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
            
            # 2. 每日/每周/每月统计数据工作表
            if stats_data:
                if group_by == 'day':
                    stats_list = []
                    for item in stats_data:
                        stats_list.append({
                            '日期': item['date'],
                            '新增用户数': item['new_users'],
                            '新增帖子总数': item['new_posts_total'],
                            '新增悬赏任务数': item.get('new_bounties', 0),
                            '新增服务任务数': item.get('new_services', 0)
                        })
                else:
                    stats_list = []
                    for item in stats_data:
                        stats_list.append({
                            '期间': item['period'],
                            '新增用户数': item['new_users'],
                            '新增帖子总数': item['new_posts_total'],
                            '新增悬赏任务数': item.get('new_bounties', 0),
                            '新增服务任务数': item.get('new_services', 0)
                        })
                
                if stats_list:
                    stats_df = pd.DataFrame(stats_list)
                    stats_df.to_excel(writer, sheet_name='详细统计数据', index=False)
            
            # 3. 用户增长趋势（用于图表）
            if stats_data and group_by == 'day':
                chart_data = []
                for item in stats_data:
                    chart_data.append({
                        '日期': item['date'],
                        '新增用户': item['new_users'],
                        '新增悬赏': item.get('new_bounties', 0),
                        '新增服务': item.get('new_services', 0)
                    })
                
                if chart_data:
                    chart_df = pd.DataFrame(chart_data)
                    chart_df.to_excel(writer, sheet_name='图表数据', index=False)
            
            # 4. 用户详细信息（如果需要）
            if data_types in ['users', 'all']:
                users_data = []
                users = User.query.filter(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                ).order_by(desc(User.created_at)).all()
                
                for user in users:
                    # 统计用户发布的帖子
                    user_posts = Post.query.filter_by(author_id=user.id).count()
                    user_bounties = Post.query.filter_by(author_id=user.id, post_type='bounty').count()
                    user_services = Post.query.filter_by(author_id=user.id, post_type='service').count()
                    
                    users_data.append({
                        '用户ID': user.id,
                        '用户名': user.username,
                        '真实姓名': user.name or '',
                        '学号': user.student_id or '',
                        '学院': user.college or '',
                        '注册时间': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                        '最后登录': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                        '积分余额': user.points,
                        '用户等级': '管理员' if user.is_admin else '普通用户',
                        '封禁状态': '是' if user.ban_until and user.ban_until >= datetime.now() else '否',
                        '封禁到期': user.ban_until.strftime('%Y-%m-%d %H:%M:%S') if user.ban_until else '',
                        '帖子总数': user_posts,
                        '悬赏任务数': user_bounties,
                        '服务任务数': user_services
                    })
                
                if users_data:
                    users_df = pd.DataFrame(users_data)
                    users_df.to_excel(writer, sheet_name='新增用户详情', index=False)
            
            # 5. 帖子详细信息（如果需要）
            if data_types in ['posts', 'all']:
                posts_data = []
                posts = Post.query.filter(
                    Post.created_at >= start_date,
                    Post.created_at <= end_date
                ).order_by(desc(Post.created_at)).all()
                
                for post in posts:
                    posts_data.append({
                        '帖子ID': post.id,
                        '标题': post.title,
                        '类型': '悬赏' if post.post_type == 'bounty' else '服务',
                        '价格': post.price,
                        '状态': '招募中' if post.status == 'active' else '进行中' if post.status == 'trading' else '已完成' if post.status == 'sold' else '已下架',
                        '创建时间': post.created_at.strftime('%Y-%m-%d %H:%M:%S') if post.created_at else '',
                        '作者ID': post.author_id,
                        '作者名': post.author.username if post.author else '',
                        '作者学号': post.author.student_id if post.author and post.author.student_id else ''
                    })
                
                if posts_data:
                    posts_df = pd.DataFrame(posts_data)
                    posts_df.to_excel(writer, sheet_name='新增帖子详情', index=False)
        
        # 移动指针到开头
        output.seek(0)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"系统统计报表_{start_date.strftime('%Y%m%d')}_至_{end_date.strftime('%Y%m%d')}_{timestamp}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return error(message=f"导出统计报表失败: {str(e)}")


# ================= 5.6 获取统计数据图表数据 =================
@admin_bp.route('/stats/charts', methods=['GET'])
@admin_required
def get_stats_charts():
    """
    为前端图表提供数据格式
    支持不同类型的图表数据
    """
    try:
        # 获取参数
        chart_type = request.args.get('type', 'line')  # line, bar, pie
        time_range = request.args.get('time_range', '7days')  # 7days, 30days, 90days
        
        # 计算时间范围 - 确保包含今天
        # 将结束日期设置为今天的23:59:59，确保包含今天的所有数据
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        if time_range == '7days':
            # 7天前，从00:00:00开始
            start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == '30days':
            start_date = (end_date - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == '90days':
            start_date = (end_date - timedelta(days=89)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = (end_date - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 查询用户统计数据
        user_stats = db.session.query(
            db.func.date(User.created_at).label('date'),
            db.func.count(User.id).label('new_users')
        ).filter(
            User.created_at >= start_date,
            User.created_at <= end_date
        ).group_by(
            db.func.date(User.created_at)
        ).order_by(
            db.func.date(User.created_at)
        ).all()
        
        # 查询帖子统计数据 - 按类型分组
        post_stats = db.session.query(
            db.func.date(Post.created_at).label('date'),
            db.func.count(Post.id).label('new_posts'),
            Post.post_type
        ).filter(
            Post.created_at >= start_date,
            Post.created_at <= end_date
        ).group_by(
            db.func.date(Post.created_at),
            Post.post_type
        ).order_by(
            db.func.date(Post.created_at)
        ).all()
        
        # 组织数据
        dates = []
        user_counts = []
        post_counts = []
        bounty_counts = []  # 悬赏任务
        service_counts = []  # 服务任务
        
        # 创建日期字典 - 使用date对象确保日期范围正确
        date_stats = {}
        current_date = start_date.date()
        end_date_date = end_date.date()
        
        while current_date <= end_date_date:
            date_str = current_date.strftime('%Y-%m-%d')
            date_stats[date_str] = {
                'users': 0,
                'posts': 0,
                'bounties': 0,
                'services': 0
            }
            dates.append(date_str)
            current_date += timedelta(days=1)
        
        # 填充用户数据
        for stat in user_stats:
            # 处理日期格式
            if isinstance(stat.date, datetime):
                date_str = stat.date.strftime('%Y-%m-%d')
            elif hasattr(stat.date, 'strftime'):
                date_str = stat.date.strftime('%Y-%m-%d')
            else:
                date_str = str(stat.date)
            
            if date_str in date_stats:
                date_stats[date_str]['users'] = stat.new_users
        
        # 填充帖子数据 - 按类型分别统计
        for stat in post_stats:
            # 处理日期格式
            if isinstance(stat.date, datetime):
                date_str = stat.date.strftime('%Y-%m-%d')
            elif hasattr(stat.date, 'strftime'):
                date_str = stat.date.strftime('%Y-%m-%d')
            else:
                date_str = str(stat.date)
            
            if date_str in date_stats:
                date_stats[date_str]['posts'] += stat.new_posts
                if stat.post_type == 'bounty':
                    date_stats[date_str]['bounties'] += stat.new_posts
                elif stat.post_type == 'service':
                    date_stats[date_str]['services'] += stat.new_posts
        
        # 转换为列表，确保顺序与dates一致
        for date_str in dates:
            user_counts.append(date_stats[date_str]['users'])
            post_counts.append(date_stats[date_str]['posts'])
            bounty_counts.append(date_stats[date_str]['bounties'])
            service_counts.append(date_stats[date_str]['services'])
        
        # 根据不同图表类型组织数据
        chart_data = {}
        
        if chart_type == 'line':
            # 折线图数据 - 趋势分析，包含所有四种数据类型
            chart_data = {
                'type': 'line',
                'title': f'系统数据趋势图 ({time_range})',
                'xAxis': {
                    'type': 'category',
                    'data': dates
                },
                'yAxis': {
                    'type': 'value',
                    'name': '数量'
                },
                'series': [
                    {
                        'name': '新增用户',
                        'type': 'line',
                        'data': user_counts,
                        'smooth': True
                    },
                    {
                        'name': '新增帖子',
                        'type': 'line',
                        'data': post_counts,
                        'smooth': True
                    },
                    {
                        'name': '悬赏任务',
                        'type': 'line',
                        'data': bounty_counts,
                        'smooth': True
                    },
                    {
                        'name': '服务任务',
                        'type': 'line',
                        'data': service_counts,
                        'smooth': True
                    }
                ]
            }
        
        elif chart_type == 'bar':
            # 柱状图数据 - 对比分析
            # 只显示最近10天的数据
            recent_dates = dates[-10:] if len(dates) > 10 else dates
            recent_users = user_counts[-10:] if len(user_counts) > 10 else user_counts
            recent_posts = post_counts[-10:] if len(post_counts) > 10 else post_counts
            recent_bounties = bounty_counts[-10:] if len(bounty_counts) > 10 else bounty_counts
            recent_services = service_counts[-10:] if len(service_counts) > 10 else service_counts
            
            chart_data = {
                'type': 'bar',
                'title': f'数据对比图 (最近{len(recent_dates)}天)',
                'xAxis': {
                    'type': 'category',
                    'data': recent_dates
                },
                'yAxis': {
                    'type': 'value',
                    'name': '数量'
                },
                'series': [
                    {
                        'name': '新增用户',
                        'type': 'bar',
                        'data': recent_users,
                        'barWidth': '40%'
                    },
                    {
                        'name': '新增帖子',
                        'type': 'bar',
                        'data': recent_posts,
                        'barWidth': '40%'
                    },
                    {
                        'name': '悬赏任务',
                        'type': 'bar',
                        'data': recent_bounties,
                        'barWidth': '40%'
                    },
                    {
                        'name': '服务任务',
                        'type': 'bar',
                        'data': recent_services,
                        'barWidth': '40%'
                    }
                ]
            }
        
        elif chart_type == 'pie':
            # 饼图数据 - 比例分析
            # 帖子类型分布
            bounty_count = Post.query.filter(
                Post.created_at >= start_date,
                Post.created_at <= end_date,
                Post.post_type == 'bounty'
            ).count()
            
            service_count = Post.query.filter(
                Post.created_at >= start_date,
                Post.created_at <= end_date,
                Post.post_type == 'service'
            ).count()
            
            post_types_data = [
                {'value': bounty_count, 'name': '悬赏任务'},
                {'value': service_count, 'name': '服务任务'}
            ]
            
            # 用户活跃度分布
            total_users = User.query.filter(
                User.created_at >= start_date,
                User.created_at <= end_date
            ).count()
            
            # 查询在指定时间范围内的活跃用户（有登录或注册的用户）
            # 注意：这里的"活跃用户"是指在时间范围内有操作的用户，用于饼图展示
            # 活跃用户 = 在时间范围内注册的用户 OR 在时间范围内有登录的用户
            active_users_in_range = User.query.filter(
                or_(
                    and_(User.created_at >= start_date, User.created_at <= end_date),  # 在时间范围内注册
                    User.last_login >= start_date  # 在时间范围内有登录
                )
            ).count()
            
            inactive_users = total_users - active_users_in_range if total_users > active_users_in_range else 0
            
            user_activity_data = [
                {'value': active_users_in_range, 'name': '活跃用户'},
                {'value': inactive_users, 'name': '非活跃用户'}
            ]
            
            chart_data = {
                'type': 'pie',
                'title': '数据分布图',
                'series': [
                    {
                        'name': '帖子类型分布',
                        'type': 'pie',
                        'radius': ['40%', '70%'],
                        'center': ['25%', '50%'],
                        'data': post_types_data,
                        'emphasis': {
                            'itemStyle': {
                                'shadowBlur': 10,
                                'shadowOffsetX': 0,
                                'shadowColor': 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    },
                    {
                        'name': '用户活跃度',
                        'type': 'pie',
                        'radius': ['40%', '70%'],
                        'center': ['75%', '50%'],
                        'data': user_activity_data,
                        'emphasis': {
                            'itemStyle': {
                                'shadowBlur': 10,
                                'shadowOffsetX': 0,
                                'shadowColor': 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            }
        
        # 计算统计摘要
        total_new_users = sum(user_counts)
        total_new_posts = sum(post_counts)
        total_new_bounties = sum(bounty_counts)
        total_new_services = sum(service_counts)
        
        # 查询活跃用户数（最近7天有操作的用户）
        # 注意：这里的"活跃用户"是指最近7天有操作的用户，与get_stats()中的"active"（可用用户）不同
        seven_days_ago = datetime.now() - timedelta(days=7)
        active_users_last_7_days = User.query.filter(
            or_(
                User.last_login >= seven_days_ago,
                User.created_at >= seven_days_ago
            )
        ).count()
        
        return success(data={
            'chart_type': chart_type,
            'time_range': time_range,
            'chart_data': chart_data,
            'summary': {
                'total_new_users': total_new_users,
                'total_new_posts': total_new_posts,
                'total_new_bounties': total_new_bounties,
                'total_new_services': total_new_services,
                'active_users_last_7_days': active_users_last_7_days
            }
        })
        
    except Exception as e:
        return error(message=f"获取图表数据失败: {str(e)}")
        # ================= 6. 导出帖子为 Excel =================
@admin_bp.route('/posts/export', methods=['GET'])
@admin_required
def export_posts_excel():
    """导出所有帖子为 Excel 文件"""
    try:
        # 获取所有帖子数据
        posts_query = db.session.query(
            Post.id,
            Post.title,
            Post.content,
            Post.price,
            Post.post_type,
            Post.status,
            Post.created_at,
            User.username.label('author_username'),
            User.name.label('author_name'),
            User.college.label('author_college')
        ).join(User, Post.author_id == User.id).order_by(desc(Post.created_at)).all()
        
        # 构建 DataFrame
        posts_data = []
        for post in posts_query:
            posts_data.append({
                'ID': post.id,
                '标题': post.title,
                '内容': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                '价格(积分)': post.price,
                '类型': '悬赏' if post.post_type == 'bounty' else '服务',
                '状态': '招募中' if post.status == 'active' else '进行中' if post.status == 'trading' else '已完成' if post.status == 'sold' else '已下架',
                '发布时间': post.created_at.strftime('%Y-%m-%d %H:%M:%S') if post.created_at else '',
                '作者用户名': post.author_username,
                '作者姓名': post.author_name or '',
                '作者学院': post.author_college or ''
            })
        
        # 如果没有数据，创建一个空的 DataFrame
        if not posts_data:
            posts_data = [{
                'ID': '',
                '标题': '暂无数据',
                '内容': '',
                '价格(积分)': '',
                '类型': '',
                '状态': '',
                '发布时间': '',
                '作者用户名': '',
                '作者姓名': '',
                '作者学院': ''
            }]
        
        df = pd.DataFrame(posts_data)
        
        # 创建 Excel 文件
        output = BytesIO()
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 写入帖子数据
                df.to_excel(writer, sheet_name='帖子数据', index=False)
                
                # 添加统计摘要
                summary_data = {
                    '统计项目': ['总帖子数', '悬赏任务数', '服务任务数', '招募中', '进行中', '已完成', '已下架'],
                    '数量': [
                        Post.query.count(),
                        Post.query.filter_by(post_type='bounty').count(),
                        Post.query.filter_by(post_type='service').count(),
                        Post.query.filter_by(status='active').count(),
                        Post.query.filter_by(status='trading').count(),
                        Post.query.filter_by(status='sold').count(),
                        Post.query.filter_by(status='deleted').count()
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
            
            # 重要：确保文件指针在开头
            output.seek(0)
            
            # 验证文件大小
            file_size = len(output.getvalue())
            if file_size == 0:
                raise Exception("生成的 Excel 文件大小为 0")
            
            # 生成文件名（使用标准格式，避免特殊字符）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"帖子数据报表_{timestamp}.xlsx"
            
            # 返回文件
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            output.close()
            raise e
    except Exception as e:
        return error(message=f"导出Excel失败: {str(e)}")




