"""
个性化推荐系统
适合学生项目的简单但有效的推荐算法
"""
from flask import Blueprint, session, request
from extensions import db
from models import Post, User, Application, Order, ViewHistory
from utils.response import success, error
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from collections import defaultdict

recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/recommendation')


def calculate_recommendation_score(user_id, post, user_preferences):
    """
    计算推荐分数
    返回：(分数, 推荐理由)
    """
    score = 0
    reasons = []
    
    # 1. 类型匹配（用户偏好的帖子类型）
    if user_preferences.get('preferred_type') == post.post_type:
        score += 30
        reasons.append("符合您偏好的帖子类型")
    
    # 2. 学院匹配（同学院或相关学院）
    user = db.session.get(User, user_id)
    if user and user.college and post.author.college:
        if user.college == post.author.college:
            score += 20
            reasons.append("同学院用户发布")
    
    # 3. 价格匹配（用户偏好的价格区间）
    preferred_price_range = user_preferences.get('preferred_price_range', [0, 100])
    if preferred_price_range[0] <= post.price <= preferred_price_range[1]:
        score += 15
        reasons.append("符合您的价格偏好")
    
    # 4. 时间衰减（新帖子加分）
    days_old = (datetime.now() - post.created_at).days
    if days_old <= 3:
        score += 10
        reasons.append("最新发布")
    elif days_old <= 7:
        score += 5
    
    # 5. 协同过滤（相似用户也喜欢的帖子）
    # 兼容处理：collaborative_score 可能是字典或整数
    collab_data = user_preferences.get('collaborative_score', {})
    if isinstance(collab_data, dict):
        collaborative_score = collab_data.get(post.id, 0)
    else:
        # 如果是整数，直接使用
        collaborative_score = collab_data if isinstance(collab_data, int) else 0
    
    if collaborative_score > 0:
        score += min(collaborative_score * 5, 25)  # 每个相似用户行为加5分，最高25分
        reasons.append("相似用户也在关注")
    
    return score, reasons


def analyze_user_preferences(user_id):
    """
    分析用户偏好
    返回用户偏好字典
    """
    preferences = {
        'preferred_type': None,
        'preferred_price_range': [0, 100],  # 默认价格区间改为 0-100
        'preferred_colleges': [],
        'collaborative_score': {}
    }
    
    # 1. 分析用户申请的帖子类型（用于类型偏好，但不用于价格计算）
    applications = Application.query.filter_by(applicant_id=user_id).all()
    
    if applications:
        type_count = defaultdict(int)
        
        for app in applications:
            post = app.post
            if post:
                type_count[post.post_type] += 1
        
        # 找出最偏好的类型
        if type_count:
            preferences['preferred_type'] = max(type_count.items(), key=lambda x: x[1])[0]
    
    # 2. 分析用户完成的订单中的价格（只使用实际完成的交易计算价格偏好）
    # 这样更准确，因为只有完成的交易才真正反映用户的价格偏好
    prices = []  # 只收集完成订单的价格数据
    orders = Order.query.filter(
        or_(Order.buyer_id == user_id, Order.seller_id == user_id)
    ).filter_by(status='completed').all()
    
    if orders:
        for order in orders:
            if order.post:
                prices.append(order.post.price)
    
    # 3. 基于用户实际完成的订单计算价格偏好区间
    # 只使用完成的订单，因为只有实际完成的交易才真正反映用户的价格偏好
    if prices:
        # 计算平均值
        avg_price = sum(prices) / len(prices)
        # 使用平均值 ± 50% 作为偏好区间，但限制在合理范围内
        min_price = max(0, int(avg_price * 0.5))
        max_price = int(avg_price * 1.5)
        # 确保最大值不超过 1000，最小值不小于 0
        preferences['preferred_price_range'] = [min_price, min(max_price, 1000)]
    else:
        # 如果没有完成的订单数据，使用默认值 0-100
        preferences['preferred_price_range'] = [0, 100]
    
    # 4. 分析用户完成的订单中的学院偏好
    if orders:
        colleges = set()
        for order in orders:
            if order.buyer_id == user_id and order.seller:
                colleges.add(order.seller.college)
            elif order.seller_id == user_id and order.buyer:
                colleges.add(order.buyer.college)
        preferences['preferred_colleges'] = list(colleges)
    
    # 5. 协同过滤：找到相似用户
    # 相似用户定义：同学院 + 有相似申请行为
    user = db.session.get(User, user_id)
    if user and user.college:
        # 找到同学院的其他用户
        similar_users = User.query.filter(
            and_(
                User.college == user.college,
                User.id != user_id
            )
        ).all()
        
        # 统计相似用户申请的帖子
        similar_posts_count = defaultdict(int)
        for similar_user in similar_users:
            similar_apps = Application.query.filter_by(applicant_id=similar_user.id).all()
            for app in similar_apps:
                if app.post:
                    similar_posts_count[app.post_id] += 1
        
        # 存储协同过滤分数
        preferences['collaborative_score'] = similar_posts_count
    
    return preferences


@recommendation_bp.route('/posts', methods=['GET'])
def get_recommendations():
    """
    获取个性化推荐帖子
    GET /recommendation/posts?limit=10
    支持所有用户（包括管理员）使用推荐功能
    """
    current_user_id = session.get('user_id')
    limit = request.args.get('limit', 10, type=int)
    if limit > 50:
        limit = 50
    
    if not current_user_id:
        # 未登录用户返回热门帖子
        hot_posts = Post.query.filter_by(status='active').order_by(
            Post.created_at.desc()
        ).limit(limit).all()
        
        return success(data={
            'recommendations': [p.to_dict() for p in hot_posts],
            'user_preferences': None,
            'message': '请登录以获取个性化推荐'
        })
    
    limit = request.args.get('limit', 10, type=int)
    if limit > 50:
        limit = 50
    
    try:
        # 1. 分析用户偏好
        user_preferences = analyze_user_preferences(current_user_id)
        
        # 2. 获取用户已申请/已完成的帖子ID（排除这些）
        excluded_post_ids = set()
        
        # 已申请的帖子
        applications = Application.query.filter_by(applicant_id=current_user_id).all()
        excluded_post_ids.update([app.post_id for app in applications if app.post_id])
        
        # 已完成的订单
        orders = Order.query.filter(
            or_(Order.buyer_id == current_user_id, Order.seller_id == current_user_id)
        ).filter_by(status='completed').all()
        excluded_post_ids.update([order.post_id for order in orders if order.post_id])
        
        # 排除自己发布的帖子
        user_posts = Post.query.filter_by(author_id=current_user_id).all()
        excluded_post_ids.update([p.id for p in user_posts])
        
        # 3. 获取所有活跃的帖子（排除已申请/已完成的）
        query = Post.query.filter(Post.status == 'active')
        if excluded_post_ids:
            query = query.filter(~Post.id.in_(excluded_post_ids))
        all_posts = query.all()
        
        # 4. 计算每个帖子的推荐分数
        scored_posts = []
        for post in all_posts:
            # 获取该帖子的协同过滤分数
            collab_dict = user_preferences.get('collaborative_score', {})
            if isinstance(collab_dict, dict):
                collaborative_score = collab_dict.get(post.id, 0)
            else:
                collaborative_score = 0
            
            # 临时设置协同过滤分数用于计算（保持字典格式）
            temp_prefs = user_preferences.copy()
            # 创建一个新的字典，只包含当前帖子的协同过滤分数
            temp_prefs['collaborative_score'] = {post.id: collaborative_score} if collaborative_score > 0 else {}
            
            score, reasons = calculate_recommendation_score(
                current_user_id, post, temp_prefs
            )
            
            if score > 0:  # 只推荐分数大于0的帖子
                scored_posts.append({
                    'post': post,
                    'score': score,
                    'reasons': reasons
                })
        
        # 5. 按分数排序，取前N个
        scored_posts.sort(key=lambda x: x['score'], reverse=True)
        top_posts = scored_posts[:limit]
        
        # 6. 格式化返回数据
        recommendations = []
        for item in top_posts:
            post_dict = item['post'].to_dict()
            post_dict['recommendation_score'] = item['score']
            post_dict['recommendation_reasons'] = item['reasons']
            recommendations.append(post_dict)
        
        # 7. 如果推荐数量不足，补充热门帖子
        if len(recommendations) < limit:
            # 获取最近7天最热门的帖子（按申请数）
            hot_posts_query = db.session.query(
                Post,
                func.count(Application.id).label('application_count')
            ).outerjoin(
                Application, Post.id == Application.post_id
            ).filter(
                and_(
                    Post.status == 'active',
                    Post.created_at >= datetime.now() - timedelta(days=7)
                )
            )
            
            if excluded_post_ids:
                hot_posts_query = hot_posts_query.filter(~Post.id.in_(excluded_post_ids))
            
            hot_posts = hot_posts_query.group_by(Post.id).order_by(
                func.count(Application.id).desc()
            ).limit(limit - len(recommendations)).all()
            
            for post, _ in hot_posts:
                if post.id not in [r['id'] for r in recommendations]:
                    post_dict = post.to_dict()
                    post_dict['recommendation_score'] = 5
                    post_dict['recommendation_reasons'] = ["热门推荐"]
                    recommendations.append(post_dict)
        
        return success(data={
            'recommendations': recommendations,
            'user_preferences': {
                'preferred_type': user_preferences.get('preferred_type'),
                'preferred_price_range': user_preferences.get('preferred_price_range')
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error(message=f"获取推荐失败：{str(e)}")


@recommendation_bp.route('/record_view', methods=['POST'])
def record_view():
    """
    记录用户浏览帖子
    POST /recommendation/record_view
    Body: {"post_id": 123}
    """
    current_user_id = session.get('user_id')
    if not current_user_id:
        return error(message="请先登录")
    
    data = request.get_json()
    if not data:
        return error(message="请提供帖子ID")
    
    post_id = data.get('post_id')
    
    if not post_id:
        return error(message="帖子ID不能为空")
    
    try:
        # 检查帖子是否存在
        post = db.session.get(Post, post_id)
        if not post:
            return error(message="帖子不存在")
        
        # 检查是否已记录
        existing = ViewHistory.query.filter_by(
            user_id=current_user_id,
            post_id=post_id
        ).first()
        
        if existing:
            # 更新查看时间
            existing.viewed_at = datetime.now()
        else:
            # 创建新记录
            view_history = ViewHistory(
                user_id=current_user_id,
                post_id=post_id
            )
            db.session.add(view_history)
        
        db.session.commit()
        return success(message="浏览记录已保存")
    
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return error(message=f"记录浏览失败：{str(e)}")

