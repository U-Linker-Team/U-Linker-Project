from flask import Blueprint, request, session
from extensions import db
from models import Post, User, PointsHistory, Favorite
from utils.response import success, error
from sqlalchemy import or_, and_, func
from datetime import datetime
import os
import uuid
market_bp = Blueprint('market', __name__, url_prefix='/market')


# ================= 1. 发布帖子 (安全加强版) =================
@market_bp.route('/add', methods=['POST'])
def add_post():
    # 1. 身份验证：只信任 Session
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    # 检查是否是管理员（管理员不能发布帖子）
    current_user = db.session.get(User, current_user_id)
    if current_user and current_user.is_admin:
        return error(message="管理员不能发布帖子")
    
    # 检查是否被封禁
    if current_user and current_user.ban_until and current_user.ban_until > datetime.now():
        ban_until_str = current_user.ban_until.strftime('%Y-%m-%d %H:%M:%S')
        return error(message=f"您的账号已被封禁至 {ban_until_str}，无法发布帖子")

        # 检查请求是否包含文件
    if 'images' in request.files:
        # 处理文件上传
        files = request.files.getlist('images')
        image_urls = []
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        
        for file in files:
            if file and file.filename:
                # 生成唯一文件名
                ext = os.path.splitext(file.filename)[1]
                filename = f"{str(uuid.uuid4())}{ext}"
                filepath = os.path.join(upload_folder, filename)
                
                # 保存文件
                file.save(filepath)
                image_urls.append(f"/uploads/{filename}")
        
        # 获取其他表单数据
        title = request.form.get('title')
        content = request.form.get('content')
        price = int(request.form.get('price', 0))
        post_type = request.form.get('post_type', 'service') # service 或 bounty
    else:
        # 处理JSON数据
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        price = data.get('price', 0)
        post_type = data.get('post_type', 'service') # service 或 bounty
        image_urls = [] # 没有上传图片
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


# ================= 2. 获取市场列表 (高级搜索版) =================
@market_bp.route('/list', methods=['GET'])
def get_posts():
    # ========== 1. 获取筛选参数 ==========
    p_type = request.args.get('type')  # 类型筛选：bounty 或 service
    keyword = request.args.get('keyword')  # 关键词搜索
    author_name = request.args.get('author_name')  # 作者名称搜索
    college = request.args.get('college')  # 学院筛选
    min_price = request.args.get('min_price', type=int)  # 最低价格
    max_price = request.args.get('max_price', type=int)  # 最高价格
    status = request.args.get('status', 'active')  # 状态筛选，默认只显示上架中的
    
    # 排序参数
    sort_by = request.args.get('sort', 'time')  # 排序字段：time 或 price
    order = request.args.get('order', 'desc')  # 排序方向：asc 或 desc
    
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)

    # ========== 2. 构建基础查询 ==========
    # 核心规则：市场大厅默认只显示 "active" (上架中) 的商品
    # 但支持通过 status 参数查询其他状态（如管理员查看）
    query = Post.query
    
    # 如果没指定 status，默认只显示 active
    if not request.args.get('status'):
        query = query.filter_by(status='active')
    elif status:
        query = query.filter_by(status=status)

    # ========== 3. 类型筛选 ==========
    if p_type:
        query = query.filter_by(post_type=p_type)

    # ========== 4. 高级关键词搜索（多字段模糊查询）==========
    # 标记是否需要 join User 表
    need_join_user = False
    
    if keyword:
        # 使用 or_ 操作符，在多个字段中搜索关键词
        # 使用 like 进行模糊匹配，%keyword% 表示包含该关键词
        keyword_pattern = f'%{keyword}%'
        
        # 构建搜索条件：标题、内容
        search_conditions = [
            Post.title.like(keyword_pattern),  # 标题模糊匹配
            Post.content.like(keyword_pattern),  # 内容模糊匹配
        ]
        
        # 如果需要搜索作者信息，需要 join User 表
        need_join_user = True
        query = query.join(User, Post.author_id == User.id)
        
        # 添加作者名称和学院的搜索条件
        search_conditions.extend([
            User.name.like(keyword_pattern),  # 作者名称模糊匹配
            User.username.like(keyword_pattern),  # 用户名模糊匹配
            User.college.like(keyword_pattern),  # 学院模糊匹配
        ])
        
        # 使用 or_ 组合所有搜索条件（只要满足其中一个就匹配）
        query = query.filter(or_(*search_conditions))

    # ========== 5. 作者名称精确/模糊搜索 ==========
    if author_name: 
        if not need_join_user:
            query = query.join(User, Post.author_id == User.id)
            need_join_user = True
        
        author_pattern = f'%{author_name}%'
        query = query.filter(
            or_(
                User.name.like(author_pattern),
                User.username.like(author_pattern)
            )
        )

    # ========== 6. 学院筛选 ==========
    if college:
        if not need_join_user:
            query = query.join(User, Post.author_id == User.id)
            need_join_user = True
        
        college_pattern = f'%{college}%'
        query = query.filter(User.college.like(college_pattern))

    # ========== 7. 价格范围筛选 ==========
    price_conditions = []
    if min_price is not None:
        price_conditions.append(Post.price >= min_price)
    if max_price is not None:
        price_conditions.append(Post.price <= max_price)
    
    # 如果有价格条件，使用 and_ 组合（必须同时满足）
    if price_conditions:
        query = query.filter(and_(*price_conditions))

    # ========== 8. 排序逻辑 ==========
    if sort_by == 'price':
        # 按价格排序
        if order == 'asc':
            query = query.order_by(Post.price.asc())
        else:
            query = query.order_by(Post.price.desc())
    else:
        # 默认按最新发布排序（时间）
        if order == 'asc':
            query = query.order_by(Post.created_at.asc())
        else:
            query = query.order_by(Post.created_at.desc())

    # ========== 9. 执行查询并分页 ==========
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


# ================= 6. 收藏功能 =================

# 添加收藏
@market_bp.route('/favorite/add', methods=['POST'])
def add_favorite():
    # 1. 登录校验
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    # 2. 获取参数
    data = request.get_json()
    post_id = data.get('post_id')
    
    if not post_id:
        return error(message="帖子ID不能为空")
    
    # 3. 检查帖子是否存在
    post = db.session.get(Post, post_id)
    if not post:
        return error(message="帖子不存在")
    
    # 4. 检查是否已经收藏
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        post_id=post_id
    ).first()
    
    if existing_favorite:
        return error(message="您已经收藏过该帖子了")
    
    # 5. 创建收藏记录（管理员也可以收藏，没有限制）
    try:
        new_favorite = Favorite(
            user_id=current_user_id,
            post_id=post_id
        )
        db.session.add(new_favorite)
        db.session.commit()
        return success(message="收藏成功", data=new_favorite.to_dict())
    except Exception as e:
        db.session.rollback()
        return error(message=f"收藏失败: {str(e)}")


# 取消收藏
@market_bp.route('/favorite/remove', methods=['POST'])
def remove_favorite():
    # 1. 登录校验
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    # 2. 获取参数
    data = request.get_json()
    post_id = data.get('post_id')
    
    if not post_id:
        return error(message="帖子ID不能为空")
    
    # 3. 查找收藏记录
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        post_id=post_id
    ).first()
    
    if not favorite:
        return error(message="您还没有收藏过该帖子")
    
    # 4. 删除收藏记录
    try:
        db.session.delete(favorite)
        db.session.commit()
        return success(message="取消收藏成功")
    except Exception as e:
        db.session.rollback()
        return error(message=f"取消收藏失败: {str(e)}")


# 获取我的收藏列表
@market_bp.route('/favorite/list', methods=['GET'])
def get_favorites():
    # 1. 登录校验
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    # 2. 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)
    
    # 3. 查询收藏列表（关联帖子信息）
    query = Favorite.query.filter_by(user_id=current_user_id)\
        .join(Post, Favorite.post_id == Post.id)\
        .order_by(Favorite.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 4. 构建返回数据
    items = []
    for fav in pagination.items:
        post = fav.post
        if post:
            post_dict = post.to_dict()
            # 确保包含作者信息
            if post.author:
                post_dict['author'] = {
                    'id': post.author.id,
                    'name': post.author.name or post.author.username,
                    'avatar': post.author.avatar,
                    'college': post.author.college
                }
            items.append(post_dict)
    
    return success(data={
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'items': items
    })


# 检查是否已收藏
@market_bp.route('/favorite/check', methods=['GET'])
def check_favorite():
    # 1. 登录校验
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    # 2. 获取参数
    post_id = request.args.get('post_id', type=int)
    
    if not post_id:
        return error(message="帖子ID不能为空")
    
    # 3. 检查是否已收藏
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        post_id=post_id
    ).first()
    
    return success(data={
        'is_favorited': favorite is not None
    })