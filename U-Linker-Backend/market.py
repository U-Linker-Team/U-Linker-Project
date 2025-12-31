from flask import Blueprint, request
from extensions import db
from models import Post, User, Order, Application, PointsHistory
from utils.response import success, error
from sqlalchemy import or_, and_
from datetime import datetime

# 创建名为 'market' 的蓝图，URL 前缀为 '/market'
market_bp = Blueprint('market', __name__, url_prefix='/market')


# ================= 1. 发布帖子功能 =================
@market_bp.route('/publish', methods=['POST'])
def publish_post():
    """
    发布"我能提供"类帖子（服务类帖子）
    请求参数：
    - author_id: 发布者ID
    - title: 帖子标题
    - content: 帖子内容
    - price: 服务价格（积分）
    - images: 图片URL（可选，JSON字符串或逗号分隔）
    - post_type: 帖子类型，'service' 或 'bounty'（默认为 'service'）
    """
    data = request.get_json()
    
    # 获取必需参数
    author_id = data.get('author_id')
    title = data.get('title')
    content = data.get('content')
    price = data.get('price', 0)
    images = data.get('images', '')
    post_type = data.get('post_type', 'service')  # 默认为服务类型
    
    # 参数验证
    if not author_id:
        return error(message="请提供发布者ID")
    if not title or not title.strip():
        return error(message="帖子标题不能为空")
    if not content or not content.strip():
        return error(message="帖子内容不能为空")
    if price < 0:
        return error(message="价格不能为负数")
    
    # 验证用户是否存在
    author = db.session.get(User, author_id)
    if not author:
        return error(message="用户不存在")
    
    # 如果是悬赏类型，需要检查积分是否足够
    if post_type == 'bounty':
        if author.points < price:
            return error(message="积分不足，无法发布悬赏")
        # 发布悬赏时冻结积分
        author.points -= price
        # 记录积分历史
        history = PointsHistory(
            user_id=author_id,
            points_change=-price,
            action='发布悬赏',
            description=f"发布悬赏任务：{title}"
        )
        db.session.add(history)
    
    try:
        # 创建帖子
        new_post = Post(
            author_id=author_id,
            title=title.strip(),
            content=content.strip(),
            price=price,
            images=images if images else None,
            post_type=post_type,
            status='active'  # 默认状态为活跃
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return success(
            data=new_post.to_dict(),
            message="发布成功" if post_type == 'service' else "悬赏发布成功，积分已冻结"
        )
    except Exception as e:
        db.session.rollback()
        print(f"发布帖子错误: {e}")
        return error(message=f"发布失败: {str(e)}")


# ================= 2. 我的发布功能 =================
@market_bp.route('/my_posts', methods=['GET'])
def get_my_posts():
    """
    获取用户发布的所有帖子
    查询参数：
    - user_id: 用户ID（必需）
    - post_type: 帖子类型筛选（可选，'service' 或 'bounty'）
    - status: 状态筛选（可选，'active', 'trading', 'sold', 'closed'）
    - page: 页码（默认1）
    - page_size: 每页数量（默认10）
    """
    user_id = request.args.get('user_id')
    post_type = request.args.get('post_type')  # 可选筛选
    status = request.args.get('status')  # 可选筛选
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)
    
    if not user_id:
        return error(message="请提供用户ID")
    
    # 验证用户是否存在
    user = db.session.get(User, user_id)
    if not user:
        return error(message="用户不存在")
    
    try:
        # 构建查询条件
        query = Post.query.filter_by(author_id=user_id)
        
        # 按类型筛选
        if post_type:
            query = query.filter_by(post_type=post_type)
        
        # 按状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 按创建时间倒序排列
        query = query.order_by(Post.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return success(data={
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'page_size': per_page,
            'items': [post.to_dict() for post in pagination.items]
        })
    except Exception as e:
        print(f"查询我的发布错误: {e}")
        return error(message=f"查询失败: {str(e)}")


# ================= 3. 更新帖子状态 =================
@market_bp.route('/update_post_status', methods=['POST'])
def update_post_status():
    """
    更新帖子状态（如下架、重新上架等）
    请求参数：
    - post_id: 帖子ID
    - user_id: 用户ID（验证权限）
    - status: 新状态（'active', 'closed', 'trading', 'sold'）
    """
    data = request.get_json()
    post_id = data.get('post_id')
    user_id = data.get('user_id')
    new_status = data.get('status')
    
    if not post_id or not user_id or not new_status:
        return error(message="参数不完整")
    
    # 验证状态值
    valid_statuses = ['active', 'closed', 'trading', 'sold']
    if new_status not in valid_statuses:
        return error(message=f"无效的状态值，可选值：{', '.join(valid_statuses)}")
    
    try:
        post = db.session.get(Post, post_id)
        if not post:
            return error(message="帖子不存在")
        
        # 验证权限：只有发布者可以修改
        if post.author_id != int(user_id):
            return error(message="无权修改此帖子")
        
        # 更新状态
        old_status = post.status
        post.status = new_status
        db.session.commit()
        
        return success(
            data=post.to_dict(),
            message=f"状态已更新：{old_status} -> {new_status}"
        )
    except Exception as e:
        db.session.rollback()
        print(f"更新帖子状态错误: {e}")
        return error(message=f"更新失败: {str(e)}")


# ================= 4. 删除帖子 =================
@market_bp.route('/delete_post', methods=['POST'])
def delete_post():
    """
    删除帖子（软删除：将状态改为 'closed'）
    请求参数：
    - post_id: 帖子ID
    - user_id: 用户ID（验证权限）
    """
    data = request.get_json()
    post_id = data.get('post_id')
    user_id = data.get('user_id')
    
    if not post_id or not user_id:
        return error(message="参数不完整")
    
    try:
        post = db.session.get(Post, post_id)
        if not post:
            return error(message="帖子不存在")
        
        # 验证权限
        if post.author_id != int(user_id):
            return error(message="无权删除此帖子")
        
        # 检查是否有进行中的订单
        active_orders = Order.query.filter_by(
            post_id=post_id
        ).filter(
            Order.status.in_(['pending', 'trading'])
        ).first()
        
        if active_orders:
            return error(message="该帖子有进行中的订单，无法删除")
        
        # 软删除：将状态改为 'closed'
        post.status = 'closed'
        db.session.commit()
        
        return success(message="帖子已删除")
    except Exception as e:
        db.session.rollback()
        print(f"删除帖子错误: {e}")
        return error(message=f"删除失败: {str(e)}")


# ================= 5. 我的接受功能 =================
@market_bp.route('/my_accepted', methods=['GET'])
def get_my_accepted():
    """
    获取用户接受的任务/服务
    包括：
    1. 作为卖家接受的服务订单（我提供的服务被购买）
    2. 作为帮手接受的悬赏任务（我申请的悬赏任务）
    
    查询参数：
    - user_id: 用户ID（必需）
    - type: 类型筛选（可选，'service' 服务订单 或 'bounty' 悬赏申请）
    - status: 状态筛选（可选）
    - page: 页码（默认1）
    - page_size: 每页数量（默认10）
    """
    user_id = request.args.get('user_id')
    filter_type = request.args.get('type')  # 'service' 或 'bounty'
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)
    
    if not user_id:
        return error(message="请提供用户ID")
    
    # 验证用户是否存在
    user = db.session.get(User, user_id)
    if not user:
        return error(message="用户不存在")
    
    try:
        result_items = []
        
        # 1. 获取作为卖家接受的服务订单（我提供的服务）
        if not filter_type or filter_type == 'service':
            service_orders = Order.query.join(Post).filter(
                and_(
                    Order.seller_id == user_id,
                    Post.post_type == 'service'
                )
            )
            
            if status:
                service_orders = service_orders.filter(Order.status == status)
            
            for order in service_orders.order_by(Order.created_at.desc()).all():
                post = order.post
                result_items.append({
                    'id': order.id,
                    'type': 'service',
                    'post_id': post.id,
                    'post_title': post.title,
                    'post_content': post.content,
                    'price': post.price,
                    'buyer': order.buyer.to_dict(),
                    'status': order.status,
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'order_type': '我提供的服务'
                })
        
        # 2. 获取作为帮手接受的悬赏任务（我申请的悬赏）
        if not filter_type or filter_type == 'bounty':
            bounty_applications = Application.query.join(Post).filter(
                and_(
                    Application.applicant_id == user_id,
                    Post.post_type == 'bounty'
                )
            )
            
            if status:
                bounty_applications = bounty_applications.filter(Application.status == status)
            
            for app in bounty_applications.order_by(Application.created_at.desc()).all():
                post = app.post
                # 检查是否被选中（有对应的订单）
                order = Order.query.filter_by(
                    post_id=post.id,
                    seller_id=user_id
                ).first()
                
                result_items.append({
                    'id': app.id,
                    'type': 'bounty',
                    'post_id': post.id,
                    'post_title': post.title,
                    'post_content': post.content,
                    'price': post.price,
                    'owner': post.author.to_dict(),
                    'application_status': app.status,
                    'order_status': order.status if order else None,
                    'order_id': order.id if order else None,
                    'created_at': app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'order_type': '我申请的悬赏',
                    'is_selected': app.status == 'selected' or (order is not None)
                })
        
        # 按创建时间倒序排序
        result_items.sort(key=lambda x: x['created_at'], reverse=True)
        
        # 手动分页
        total = len(result_items)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = result_items[start:end]
        
        return success(data={
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page,
            'page_size': per_page,
            'items': paginated_items
        })
    except Exception as e:
        print(f"查询我的接受错误: {e}")
        return error(message=f"查询失败: {str(e)}")


# ================= 6. 获取帖子详情 =================
@market_bp.route('/post_detail', methods=['GET'])
def get_post_detail():
    """
    获取帖子详细信息
    查询参数：
    - post_id: 帖子ID（必需）
    """
    post_id = request.args.get('post_id')
    
    if not post_id:
        return error(message="请提供帖子ID")
    
    try:
        post = db.session.get(Post, post_id)
        if not post:
            return error(message="帖子不存在")
        
        # 获取申请数量（如果是悬赏）
        application_count = 0
        if post.post_type == 'bounty':
            application_count = Application.query.filter_by(post_id=post_id).count()
        
        # 获取订单信息
        orders = Order.query.filter_by(post_id=post_id).all()
        
        post_data = post.to_dict()
        post_data['application_count'] = application_count
        post_data['order_count'] = len(orders)
        post_data['images'] = post.images.split(',') if post.images else []
        
        return success(data=post_data)
    except Exception as e:
        print(f"获取帖子详情错误: {e}")
        return error(message=f"查询失败: {str(e)}")


