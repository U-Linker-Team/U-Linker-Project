from flask import Blueprint, request, session
from extensions import db
from models import Post, User, PointsHistory
from utils.response import success, error
from sqlalchemy import or_

market_bp = Blueprint('market', __name__, url_prefix='/market')


# ================= 1. 发布帖子 (安全加强版) =================
@market_bp.route('/add', methods=['POST'])
def add_post():
    # 1. 身份验证：只信任 Session
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    price = data.get('price', 0)
    post_type = data.get('post_type', 'service') # service 或 bounty

    if not title:
        return error(message="标题不能为空")

    # 获取用户对象
    user = db.session.get(User, current_user_id)
    if not user:
        return error(message="账户状态异常")

    try:
        # 逻辑分支：如果是悬赏任务 (Bounty)
        # 规则：发布时必须立即扣除积分（托管到平台）
        if post_type == 'bounty':
            if price < 0:
                return error(message="悬赏金额不能为负数")
            
            if user.points < price:
                return error(message="您的积分不足，无法发布该悬赏")
            
            # 扣除积分
            user.points -= price

            # 记录流水
            if price > 0:
                history = PointsHistory(
                    user_id=current_user_id,
                    points_change=-price, # 负数代表支出
                    action='发布悬赏',
                    description=f"发布悬赏任务《{title}》，预扣除积分"
                )
                db.session.add(history)
        
        # 创建帖子
        new_post = Post(
            author_id=current_user_id, # 确保作者是当前登录者
            title=title,
            content=content,
            price=price,
            post_type=post_type,
            status='active' # 默认为上架状态
        )
        db.session.add(new_post)
        db.session.commit()
        return success(message="发布成功", data=new_post.to_dict())

    except Exception as e:
        db.session.rollback()
        return error(message=f"发布失败: {str(e)}")


# ================= 2. 获取市场列表 (公共区域) =================
@market_bp.route('/list', methods=['GET'])
def get_posts():
    # 筛选参数
    p_type = request.args.get('type')  
    keyword = request.args.get('keyword') 
    sort_by = request.args.get('sort') 
    order = request.args.get('order', 'desc')
    
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)

    # 核心规则：市场大厅只显示 "active" (上架中) 的商品
    query = Post.query.filter_by(status='active')

    # A. 类型筛选
    if p_type:
        query = query.filter_by(post_type=p_type)

    # B. 关键词搜索
    if keyword:
        rule = or_(Post.title.contains(keyword), Post.content.contains(keyword))
        query = query.filter(rule)

    # C. 排序
    if sort_by == 'price':
        if order == 'asc':
            query = query.order_by(Post.price.asc())
        else:
            query = query.order_by(Post.price.desc())
    else:
        # 默认按最新发布排序
        if order == 'asc':
            query = query.order_by(Post.created_at.asc())
        else:
            query = query.order_by(Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return success(data={
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'items': [post.to_dict() for post in pagination.items]
    })


# ================= 3. 获取详情 =================
@market_bp.route('/detail/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    # 1. 获取帖子
    post = db.session.get(Post, post_id)
    if not post:
        return error(message="帖子不存在")

    # 2. 准备基础数据
    post_data = post.to_dict()

    # 3. 【新增】注入作者详细信息 (满足需求：展示发布者信息)
    # 这样前端不用再发请求去查作者是谁
    if post.author:
        post_data['author_info'] = {
            'id': post.author.id,
            'name': post.author.name or post.author.username,
            'avatar': post.author.avatar,
            'college': post.author.college
        }
    
    # 4. 【新增】注入申请记录 (满足需求：申请记录展示区域)
    if post.post_type == 'bounty':
        # 优化点 A: 直接使用反向引用 post.applications，不需要手动 query Application 表
        # 优化点 B: 直接使用 app.applicant，不需要手动 get User 表
        
        app_list = []
        # 注意：这里直接遍历 post.applications
        for app in post.applications:
            # 这里的 app.applicant 是由 Application 模型里的 relationship 自动获取的
            if app.applicant:
                app_list.append({
                    
                    'application_id': app.id,
                    'applicant_id': app.applicant.id,
                    'applicant_name': app.applicant.name or app.applicant.username,
                    'applicant_avatar': app.applicant.avatar,
                    'college': app.applicant.college,
                    'message': app.message,
                    'status': app.status,
                    'time': app.created_at.strftime('%Y-%m-%d %H:%M')
                })
        
        post_data['applications'] = app_list

    return success(data=post_data)


# ================= 4. 我的发布 / 管理员管理发布 =================
@market_bp.route('/my_published', methods=['GET'])
def get_my_published():
    # 1. 登录校验
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    current_user = db.session.get(User, current_user_id)
    
    # 2. 确定查询目标
    # 前端没传 user_id -> 查自己
    # 前端传了 user_id -> 检查权限
    target_user_id = request.args.get('user_id', type=int)
    if not target_user_id:
        target_user_id = current_user_id 

    # 3. 权限控制
    if target_user_id != current_user_id:
        if not current_user.is_admin:
            return error(message="权限不足：无法查看他人的发布记录")

    # 4. 执行查询
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)

    # 注意：个人中心/管理后台应该能看到所有状态的帖子（包括 sold, trading, active, deleted）
    query = Post.query.filter_by(author_id=target_user_id).order_by(Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'target_user_id': target_user_id,
        'items': [p.to_dict() for p in pagination.items]
    })


# ================= 5. 删除/下架帖子 (核心逻辑完善版) =================
@market_bp.route('/delete', methods=['POST'])
def delete_post():
    # 1. 登录校验
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    data = request.get_json()
    post_id = data.get('post_id')
    
    post = db.session.get(Post, post_id)
    if not post:
        return error(message="帖子不存在")
    
    current_user = db.session.get(User, current_user_id)

    # 2. 权限校验：作者本人 或 管理员 可删
    if post.author_id != current_user_id and not current_user.is_admin:
        return error(message="您无权操作此帖子")

    # 3. 状态检查 (防止误删重要交易)
    if post.status == 'trading':
        return error(message="当前订单正在交易中，无法直接删除。请先前往订单中心取消订单。")
    
    if post.status == 'sold':
        # 已售出的商品通常允许删除（逻辑删除），或者不允许
        # 这里为了数据完整性，我们可以允许删除，只是前端不再显示
        pass 

    if post.status == 'deleted':
        return error(message="该帖子已经被删除了，请勿重复操作")

    # 4. 执行删除逻辑
    try:
        # --- 核心逻辑：悬赏退款 ---
        # 如果是悬赏任务 (bounty)，且状态是 'active' (说明没人接单，或者接单还没确认)
        # 此时删除，必须把预扣的钱退给作者
        if post.post_type == 'bounty' and post.status == 'active':
            # 注意：如果管理员删了用户的违规帖，钱也应该退给作者（作者才是钱的主人）
            author = db.session.get(User, post.author_id)
            
            if post.price > 0:
                author.points += post.price
                
                # 记录退款流水
                refund_history = PointsHistory(
                    user_id=author.id,
                    points_change=post.price, # 正数代表退回
                    action='撤销悬赏',
                    description=f"悬赏任务《{post.title}》已下架/删除，积分自动退回"
                )
                db.session.add(refund_history)

        # --- 状态变更 (软删除) ---
        # 我们不真的从数据库 delete，而是标记为 deleted
        # 这样以后还能查账
        post.status = 'deleted'

        db.session.commit()
        return success(message="帖子已下架，如有预扣积分已自动退回")

    except Exception as e:
        db.session.rollback()
        return error(message=f"删除失败: {str(e)}")
