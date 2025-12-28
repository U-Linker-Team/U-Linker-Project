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
