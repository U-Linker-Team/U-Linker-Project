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
