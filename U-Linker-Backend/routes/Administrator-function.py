# ================= 根据学号获取用户全景记录 =================
@admin_bp.route('/users/by_student_id/<string:sid>', methods=['GET'])
@admin_required
def get_user_by_student_id(sid):
    # ... (省略中间查找用户的代码) ...
    
    # 对应功能：搜索该用户的“我需要”(悬赏) 帖子
    i_need = Post.query.filter_by(author_id=user.id, post_type='bounty').order_by(desc(Post.created_at)).all()
    
    # 对应功能：搜索该用户的“我能提供”(服务) 帖子
    i_provide = Post.query.filter_by(author_id=user.id, post_type='service').order_by(desc(Post.created_at)).all()

    # ...
    return success(data={
        'user_info': user.to_dict(),
        'posts': {
            'i_need': [p.to_dict() for p in i_need],      # 前端拿到这个显示“我需要”
            'i_provide': [p.to_dict() for p in i_provide] # 前端拿到这个显示“我能”
        },
        # ...
    })

# ================= 获取所有帖子列表 =================
@admin_bp.route('/posts', methods=['GET'])
@admin_required
def get_all_posts():
    # ...
    # 对应功能：帖子管理列表查询
    query = Post.query.join(User, Post.author_id == User.id)
    
    # 对应功能：搜索帖子（支持标题、内容、作者名）
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
    # ...