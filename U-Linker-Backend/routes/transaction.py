from flask import Blueprint, request,session
from extensions import db
from models import Order, Post, User, Application
from utils.response import success, error
from sqlalchemy import or_
from models import PointsHistory
from datetime import datetime, timedelta
from calendar import monthrange

transaction_bp = Blueprint('transaction', __name__, url_prefix='/transaction')


# ================= 场景 A: 购买服务 (Service Flow) =================
# 买家直接购买，扣买家的钱
@transaction_bp.route('/purchase', methods=['POST'])
def purchase_service():
    buyer_id = session.get('user_id')
    if not buyer_id:
        return error(message="请先登录")

    data = request.get_json()
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

        # 2.记录积分历史
        history = PointsHistory(
            user_id=buyer_id,
            points_change=-post.price,
            action='购买服务',
            description=f"购买了商品 {post.title}"
        )
        db.session.add(history)

        # 3. 生成订单
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

# 1. 帮手申请任务 
@transaction_bp.route('/apply', methods=['POST'])
def apply_for_task():
    applicant_id = session.get('user_id')
    if not applicant_id:
        return error(message="请先登录")
    
    data = request.get_json()
    
    post_id = data.get('post_id')
    apply_msg = data.get('message','')
    post = db.session.get(Post, post_id)
    if not post or post.post_type != 'bounty':
        return error(message="该帖子不支持申请")

    if post.status != 'active':
        return error(message="任务招募已结束")

    # 检查是否重复申请 
    exist = Application.query.filter_by(post_id=post_id, applicant_id=applicant_id).first()
    if exist:
        return error(message="您已经申请过该任务了")

    # 记录积分历史（如果有相关的积分变动）
    history = PointsHistory(
        user_id=applicant_id,
        points_change=0,  # 无积分变动
        action="申请悬赏任务",
        description=f"申请任务 {post.title}"
    )

    db.session.add(history)
    app = Application(post_id=post_id, applicant_id=applicant_id,message=apply_msg)
    db.session.add(app)
    db.session.commit()
    return success(message="申请成功，等待雇主确认")

# 2. 雇主选人帮忙(1对多的) 
@transaction_bp.route('/select_helper', methods=['POST'])
def select_helper():
    current_user_id = session.get('user_id') # 获取当前操作人
    if not current_user_id:
        return error(message="请先登录")
    
    data = request.get_json()
    owner_id = data.get('owner_id')  # 当前操作人(雇主)
    if current_user_id != owner_id:
        return error(message="您无权操作他人的悬赏任务")

    post_id = data.get('post_id')
    helper_id = data.get('helper_id')  # 选中的帮手
    post = db.session.get(Post, post_id)
    owner = db.session.get(User,owner_id) #获取雇主对象

    if not post or post.author_id != owner_id:
        return error(message="无权操作")

    #检查雇主是否有足够的钱支付悬赏
    if owner.points < post.price:
        return error(message="您的积分不足以支付该悬赏任务")
    
    try:
        # 1. 生成订单 (注意：钱在发布时已经扣了，这里不用再扣)
        new_order = Order(
            buyer_id=owner_id,  # 雇主是买单的人
            seller_id=helper_id,  # 帮手是赚钱的人
            post_id=post_id,
            status='pending'
        )

        #2. 记录积分历史 - 雇主支付积分给帮手
        history = PointsHistory(
            user_id=owner_id,
            points_change=0,  # 假设任务价格是post.price
            action="选择帮手",
            description=f"雇主 {owner_id} 支付积分给帮手 {helper_id}, 任务进入进行中的状态"
        )
        db.session.add(history)

        # 3. 更新状态
        post.status = 'trading'  # 任务进行中

        # 4. 标记申请状态为已选中
        app = Application.query.filter_by(post_id=post_id, applicant_id=helper_id).first()
        if app: app.status = 'selected'

        db.session.add(new_order)
        db.session.commit()
        return success(message="已确认帮手，积分已扣除, 任务开始", data=new_order.to_dict())
    except Exception as e:
        db.session.rollback()
        return error(message=str(e))


# ================= 通用接口 =================

# 确认完成 
@transaction_bp.route('/confirm_complete', methods=['POST'])
def confirm_complete():
    user_id = session.get('user_id')  # 操作人
    if not user_id:
        return error(message="请先登录")

    data = request.get_json()
    order_id = data.get('order_id')
    
    order = db.session.get(Order, order_id)
    if not order or order.status != 'pending': return error(message="订单状态异常")

    # 规则：
    # 如果是服务(Service)，只有卖家(提供者)能确认完成 
    # 如果是悬赏(Bounty)，只有买家(雇主)能确认完成 

    is_service = (order.post.post_type == 'service')
    can_confirm = False

    if is_service and order.seller_id == user_id: can_confirm = True #卖家确认发货
    if not is_service and order.buyer_id == user_id: can_confirm = True #雇主确认收货

    if not can_confirm:
        return error(message="您无权确认此订单")

    try:
        # 转账给卖家(赚钱的人)
        seller = db.session.get(User, order.seller_id)
        seller.points += order.post.price

        # 记录积分历史 - 卖家收到支付积分
        history = PointsHistory(
            user_id=order.seller_id,
            points_change=order.post.price,
            action="任务完成",
            description=f"卖家 {order.seller_id} 收到支付的积分{order.post.price}，任务已完成"
        )

        db.session.add(history)
        order.status = 'completed'
        order.post.status = 'sold'
        db.session.commit()
        return success(message="交易完成，积分已结算")
    except Exception as e:
        db.session.rollback()
        return error(message=str(e))

#新增的取消订单的窗口 这个取消订单逻辑核心: 把钱退给支付方 
@transaction_bp.route('/cancel_order', methods=['POST'])
def cancel_order():
    user_id = session.get('user_id') 
    if not user_id:
        return error(message="请先登录")

    data = request.get_json()
    order_id = data.get('order_id')
    order = db.session.get(Order, order_id)
    if not order:
        return error(message="订单不存在")
    
    if order.status != 'pending':
        return error(message="只有进行中的订单才能取消")

    # 获取当前时间
    now = datetime.now()
    # 订单创建了多久
    duration = now - order.created_at 
    
    # 1. 卖家/帮手 (Seller) 想要取消
    if user_id == order.seller_id:
        # 卖家随时可以取消，视为“放弃接单/无法发货”
        pass # 直接放行，进入下方的退款流程

    # 2. 买家/雇主 (Buyer) 想要取消
    elif user_id == order.buyer_id:
        # 定义时间阈值
        grace_period = timedelta(minutes=30) # 冷静期(30mins以内)
        timeout_limit = timedelta(hours=48)  # 超时保护期(>48hours)

        if duration < grace_period:
            # 如果是刚下的单（30分钟内），允许买家反悔
            pass 
        elif duration > timeout_limit:
            # 如果超过48小时还是 pending，说明卖家没动静，允许买家撤单
            pass
        else:
            # 既不是刚下单，也没超时，禁止买家单方面取消
            return error(message="卖家可能正在服务中，请联系卖家协商取消，或等待48小时后自动解锁。")

    else:
        # 既不是买家也不是卖家
        return error(message="您无权操作此订单")

    # ============ 执行退款流程 (逻辑不变) ============
    try:
        # 谁出的钱，退给谁 (Buyer)
        refund_amount = order.post.price
        payer = db.session.get(User, order.buyer_id)
        
        # 退款
        payer.points += refund_amount

        # 记录日志
        history = PointsHistory(
            user_id=payer.id,
            points_change=refund_amount,
            action='订单取消',
            description=f"订单 {order.id} 取消（操作人: {user_id}），退款 {refund_amount}"
        )
        db.session.add(history)

        order.status = 'cancelled'
        order.post.status = 'active' # 恢复帖子让别人能买/能接

        db.session.commit()
        return success(message="订单已取消，积分已退回")

    except Exception as e:
        db.session.rollback()
        return error(message=f"取消失败: {str(e)}")


#表示用户参与的情况
@transaction_bp.route('/my_involved', methods=['GET'])
def get_my_involved():
    # 1. 安全校验：获取当前登录用户
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    current_user = db.session.get(User, current_user_id)
    if not current_user:
        return error(message="账户异常")

    # 2. 确定“目标用户” (到底要查谁的订单？)
    # 前端传来 user_id，说明想查特定的人
    target_user_id = request.args.get('user_id', type=int)

    # 如果前端没传 user_id，默认查当前登录者自己
    if not target_user_id:
        target_user_id = current_user_id

    # 3. 核心权限控制 (Gatekeeper)
    # 只有两种情况允许查询：
    # A. 查自己 (target == current)
    # B. 管理员查别人 (current.is_admin is True)
    if target_user_id != current_user_id:
        if not current_user.is_admin:
            return error(message="权限不足：您不能查看他人的交易记录")

    # 4. 获取目标用户信息 (为了让管理员知道在查谁，优化体验)
    target_user_info = None
    if target_user_id == current_user_id:
        target_user_info = current_user.to_dict()
    else:
        # 如果是管理员查别人，去数据库捞一下这个人的资料
        target_obj = db.session.get(User, target_user_id)
        if target_obj:
            target_user_info = target_obj.to_dict()
        else:
            return error(message="查询的目标用户不存在")

    #4.逻辑升级: 支持filter参数: "published"(我发布的/我买的) 和"accepted(我接受的，我卖的)
    role_filter = request.args.get('role') #published|accepted

    query = Order.query
    if role_filter == 'published':
        #我是买家(对于悬赏是雇主 对于服务是消费者)
        query = query.filter(Order.buyer_id == target_user_id)
    elif role_filter == 'accepted':
        # 我是卖家 (对于悬赏是帮手，对于服务是提供者)
        query = query.filter(Order.seller_id == target_user_id)
    else:
        # 没传参数，就查所有参与的
        query = query.filter(
            or_(Order.buyer_id == target_user_id, Order.seller_id == target_user_id)
        )

    query = query.order_by(Order.created_at.desc())
    # 6. 分页返回
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'role_filter': role_filter,
        'items': [o.to_dict() for o in pagination.items],
        'target_user': target_user_info # 返回当前正在查看的用户信息
    })

@transaction_bp.route('/points/history', methods=['GET'])
def get_points_history():
    # 1. 登录检查
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="未登录")
    
    current_user = db.session.get(User, current_user_id)
    if not current_user:
        return error(message="账户异常")

    # 2. 确定要查的目标 ID
    target_user_id = request.args.get('user_id', type=int)
    if not target_user_id:
        target_user_id = current_user_id # 没传就默认查自己

    # 3. 权限控制 (Gatekeeper)
    if target_user_id != current_user_id:
        if not current_user.is_admin:
            return error(message="无权查看他人信息")

    # 获取目标用户的基本信息 (为了让前端显示方便)
    # 如果查的是自己，直接用 current_user；如果查别人，去数据库捞一下
    target_user_info = None
    if target_user_id == current_user_id:
        target_user_info = current_user.to_dict()
    else:
        # 管理员查别人，需要把那个人的信息也查出来
        target_obj = db.session.get(User, target_user_id)
        if target_obj:
            target_user_info = target_obj.to_dict()
        else:
            return error(message="查询的目标用户不存在")

    # 5. 查询积分流水 (通用逻辑)
    query = PointsHistory.query.filter_by(user_id=target_user_id)

    # ... (时间筛选逻辑保持不变) ...
    period = request.args.get('period', 'all')
    if period != 'all':
        now = datetime.now()
        if period == 'current':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(PointsHistory.created_at >= start_date)
        elif period == 'last':
            first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month_day = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_month_day.replace(day=1, hour=0, minute=0, second=0)
            query = query.filter(PointsHistory.created_at >= first_day_last_month,
                                 PointsHistory.created_at < first_day_this_month)
        elif period == '3months':
            start_date = now - timedelta(days=90)
            query = query.filter(PointsHistory.created_at >= start_date)

    # 6. 排序分页
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)
    
    query = query.order_by(PointsHistory.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'items': [h.to_dict() for h in pagination.items],
        
        # 告诉前端查的是谁的信息
        'target_user': target_user_info 
    })



