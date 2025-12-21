from flask import Blueprint, request
from extensions import db
from models import Post, User
from utils.response import success, error
from sqlalchemy import or_  # <--- 新增导入：用于复杂的查询逻辑

# 创建名为'market'的蓝图，所有路由将以'/market'为前缀
market_bp = Blueprint('market', __name__, url_prefix='/market')


# 1. 发布帖子 (保持不变，含扣分逻辑)
@market_bp.route('/add', methods=['POST'])
def add_post():
    data = request.get_json()
    author_id = data.get('author_id')
    title = data.get('title')
    content = data.get('content')
    price = data.get('price', 0)
    post_type = data.get('post_type', 'service')

    # 参数校验：检查必填字段是否为空
    if not all([author_id, title]):
        return error(message="缺少必要参数")

    # 检查用户是否存在
    user = db.session.get(User, author_id)
    if not user:
        return error(message="用户不存在")

    try:
        # SRS 5.1.4.2: 如果是悬赏，发布时必须冻结/扣除积分
        if post_type == 'bounty':
            if user.points < price:
                return error(message="积分不足，无法发布悬赏")
            user.points -= price  # 立即扣除

        new_post = Post(
            author_id=author_id,
            title=title,
            content=content,
            price=price,
            post_type=post_type,
            status='active'
        )
        db.session.add(new_post)
        db.session.commit()
        return success(message="发布成功", data=new_post.to_dict())

    except Exception as e:
        db.session.rollback()
        print(e)
        return error(message="发布失败")


# 2. 获取列表 (升级版：支持搜索和排序 SRS 5.1.3 & 5.2.3)
@market_bp.route('/list', methods=['GET'])
def get_posts():
    # 获取参数
    p_type = request.args.get('type')  # 筛选类型: service, bounty
    keyword = request.args.get('keyword')  # 搜索关键词
    sort_by = request.args.get('sort')  # 排序依据: time(默认), price
    order = request.args.get('order', 'desc')  # 排序方向: desc(降序), asc(升序)

    #获得分页参数(新增)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('page_size', 10, type=int)

    # 基础查询：只看活跃的
    query = Post.query.filter_by(status='active')

    # A. 类型筛选
    if p_type:
        query = query.filter_by(post_type=p_type)

    # B. 关键词搜索 (标题 或 内容)
    if keyword:
        rule = or_(Post.title.contains(keyword), Post.content.contains(keyword))
        query = query.filter(rule)

    # C. 排序逻辑
    if sort_by == 'price' or sort_by == 'points':
        # 按价格/积分排序
        if order == 'asc':
            query = query.order_by(Post.price.asc())
        else:
            query = query.order_by(Post.price.desc())
    else:
        # 默认按时间排序
        if order == 'asc':
            query = query.order_by(Post.created_at.asc())
        else:
            query = query.order_by(Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return success(data={
        'total': pagination.total,       # 总条数
        'pages': pagination.pages,       # 总页数
        'current_page': page,            # 当前页码
        'items': [post.to_dict() for post in pagination.items] # 当前页的数据列表
    })

@market_bp.route('/my_published', methods=['GET'])
def get_my_published():
    user_id = request.args.get('user_id')
    if not user_id:
        return error(message="请提供user_id")
    
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('page_size',10,type=int)

    query = Post.query.filter_by(author_id = user_id).order_by(Post.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'items': [p.to_dict() for p in pagination.items]

    })
