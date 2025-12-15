from flask import Blueprint, request
from extensions import db
from models import Order, Post, User, Application
from utils.response import success, error
from sqlalchemy import or_

transaction_bp = Blueprint('transaction', __name__, url_prefix='/transaction')


# ================= 场景 A: 购买服务 (Service Flow) =================
# SRS 5.1.5.2: 买家直接购买，扣买家的钱
@transaction_bp.route('/purchase', methods=['POST'])
def purchase_service():
    data = request.get_json()
    buyer_id = data.get('buyer_id')
    post_id = data.get('post_id')

    buyer = db.session.get(User, buyer_id)
    post = db.session.get(Post, post_id)

    if not buyer or not post: return error(message="参数错误")
    if post.post_type != 'service': return error(message="这不是服务，不能直接购买")
    if post.status != 'active': return error(message="手慢了！商品不可用")
    if post.author_id == buyer.id: return error(message="不能买自己的服务")
    if buyer.points < post.price: return error(message="积分不足")

    try:
        # 1. 扣买家的钱
        buyer.points -= post.price

        # 2. 生成订单
        new_order = Order(
            buyer_id=buyer_id,  # 买家是消费者
            seller_id=post.author_id,  # 作者是服务提供者
            post_id=post_id,
            status='pending'
        )
        post.status = 'trading'  # 锁定商品

        db.session.add(new_order)
        db.session.commit()
        return success(message="购买成功，积分已冻结", data=new_order.to_dict())
    except Exception as e:
        db.session.rollback()
        return error(message=str(e))


# ================= 场景 B: 悬赏任务 (Bounty Flow) =================

# 1. 申请任务 (SRS 5.1.5.1.1)
@transaction_bp.route('/apply', methods=['POST'])
def apply_for_task():
    data = request.get_json()
    applicant_id = data.get('applicant_id')
    post_id = data.get('post_id')

    post = db.session.get(Post, post_id)
    if not post or post.post_type != 'bounty':
        return error(message="该帖子不支持申请")

    if post.status != 'active':
        return error(message="任务招募已结束")

    # 检查是否重复申请 (SRS 304)
    exist = Application.query.filter_by(post_id=post_id, applicant_id=applicant_id).first()
    if exist:
        return error(message="您已经申请过该任务了")

    app = Application(post_id=post_id, applicant_id=applicant_id)
    db.session.add(app)
    db.session.commit()
    return success(message="申请成功，等待雇主确认")


# 2. 雇主选人 (SRS 5.1.5.1.3)
@transaction_bp.route('/select_helper', methods=['POST'])
def select_helper():
    data = request.get_json()
    owner_id = data.get('owner_id')  # 当前操作人(雇主)
    post_id = data.get('post_id')
    helper_id = data.get('helper_id')  # 选中的帮手

    post = db.session.get(Post, post_id)
    if not post or post.author_id != owner_id:
        return error(message="无权操作")

    try:
        # 1. 生成订单 (注意：钱在发布时已经扣了，这里不用再扣)
        new_order = Order(
            buyer_id=owner_id,  # 雇主是买单的人
            seller_id=helper_id,  # 帮手是赚钱的人
            post_id=post_id,
            status='pending'
        )

        # 2. 更新状态
        post.status = 'trading'  # 任务进行中

        # 3. 标记申请状态为已选中
        app = Application.query.filter_by(post_id=post_id, applicant_id=helper_id).first()
        if app: app.status = 'selected'

        db.session.add(new_order)
        db.session.commit()
        return success(message="已确认帮手，任务开始", data=new_order.to_dict())
    except Exception as e:
        db.session.rollback()
        return error(message=str(e))


# ================= 通用接口 =================

# 确认完成 (通用 SRS 5.1.5.1.4 & 5.1.5.2.3)
@transaction_bp.route('/confirm_complete', methods=['POST'])
def confirm_complete():
    data = request.get_json()
    order_id = data.get('order_id')
    user_id = data.get('user_id')  # 操作人

    order = db.session.get(Order, order_id)
    if not order or order.status != 'pending': return error(message="订单状态异常")

    # 规则：
    # 如果是服务(Service)，只有卖家(提供者)能确认完成 [cite: 318]
    # 如果是悬赏(Bounty)，只有买家(雇主)能确认完成 [cite: 311]

    is_service = (order.post.post_type == 'service')
    can_confirm = False

    if is_service and order.seller_id == user_id: can_confirm = True
    if not is_service and order.buyer_id == user_id: can_confirm = True

    if not can_confirm:
        return error(message="您无权确认此订单")

    try:
        # 转账给卖家(赚钱的人)
        seller = db.session.get(User, order.seller_id)
        seller.points += order.post.price

        order.status = 'completed'
        order.post.status = 'sold'
        db.session.commit()
        return success(message="交易完成，积分已结算")
    except Exception as e:
        db.session.rollback()
        return error(message=str(e))

@transaction_bp.route('/my_involved', methods=['GET'])
def get_my_involved():
    user_id = request.args.get('user_id')
    if not user_id:
        return error(message="请提供 user_id")

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)

    # 核心逻辑: 只要 buyer_id 是我，或者 seller_id 是我，都算我参与的
    query = Order.query.filter(
        or_(Order.buyer_id == user_id, Order.seller_id == user_id)
    ).order_by(Order.created_at.desc())

    # 分页返回
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'items': [o.to_dict() for o in pagination.items]
    })