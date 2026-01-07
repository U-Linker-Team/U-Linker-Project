from extensions import db
from datetime import datetime

# --- 1. 用户模型 ---
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)  # 增加到512以支持scrypt长哈希
    name = db.Column(db.String(50))
    college = db.Column(db.String(50))
    student_id = db.Column(db.String(20), unique=True)
    points = db.Column(db.Integer, default=100)
    avatar = db.Column(db.String(200))
    failed_login_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    ban_until = db.Column(db.DateTime)  # 封禁到期时间，None 表示未封禁
    ban_count = db.Column(db.Integer, default=0)  # 封禁次数，用于计算封禁时长
    created_at = db.Column(db.DateTime, default=datetime.now)  # 用户注册时间
    last_login = db.Column(db.DateTime)  # 最后登录时间

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            # 学号：同时返回 snake_case 和 camelCase 以兼容前端不同命名风格
            'student_id': self.student_id,
            'studentId': self.student_id or '',  # camelCase 格式，JavaScript 标准
            'points': self.points,
            'avatar': self.avatar,
            'college': self.college,
            'is_admin': self.is_admin,
            'ban_until': self.ban_until.strftime('%Y-%m-%d %H:%M:%S') if self.ban_until else None,
            'is_banned': self.ban_until is not None and self.ban_until > datetime.now() if self.ban_until else False,
            'ban_count': self.ban_count or 0,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }
# --- 2. 帖子模型 ---
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, default=0)
    images = db.Column(db.Text)
    post_type = db.Column(db.String(20), default='service', nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)

    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'author': self.author.to_dict(),
            'title': self.title,
            'content': self.content,
            'price': self.price,
            'post_type': self.post_type,
            'status': self.status,
            'images': self.images,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# --- 3. 申请记录模型 ---
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    message = db.Column(db.String(200),default='')
    created_at = db.Column(db.DateTime, default=datetime.now)
    post = db.relationship('Post', backref=db.backref('applications', lazy=True, cascade="all,delete-orphan"))
    applicant = db.relationship('User', backref=db.backref('my_applications', lazy=True))
    # 联合唯一索引
    __table_args__ = (
        db.UniqueConstraint('post_id', 'applicant_id', name='unique_user_application'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'applicant_id': self.applicant_id,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            # 方便前端直接拿到申请人的头像和名字
            'applicant_info': {
                'id': self.applicant.id,
                'name': self.applicant.name or self.applicant.username,
                'avatar': self.applicant.avatar,
                'college': self.applicant.college
            } if self.applicant else None
        }

# --- 4. 订单模型 ---
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_orders')
    post = db.relationship('Post', backref='orders')

    def to_dict(self):
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'post_title': self.post.title,
            'price': self.post.price,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            # 1. 必须返回关联的帖子信息
            'post': {
                'id': self.post.id,
                'title': self.post.title,
                'price': self.post.price,
                'post_type': self.post.post_type, # service 或 bounty
            } if self.post else None,

            # 2. 必须返回买家信息 (用于显示雇主/消费者)
            'buyer_info': {
                'id': self.buyer.id,
                'name': self.buyer.name or self.buyer.username,
                'avatar': self.buyer.avatar,
                'college': self.buyer.college
            } if self.buyer else None,

            # 3. 必须返回卖家信息 (用于显示帮手/服务者)
            'seller_info': {
                'id': self.seller.id,
                'name': self.seller.name or self.seller.username,
                'avatar': self.seller.avatar,
                'college': self.seller.college
            } if self.seller else None
        }

# --- 5. 聊天会话模型 (新增) ---
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.Integer, primary_key=True)
    # 为了简化，规定 user1_id 总是小于 user2_id，防止重复创建
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now) # 只要有新消息就更新这个时间

    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])

# --- 6. 消息模型 (新增) ---
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500))  # 文本内容，可为空（如果是图片/视频）
    message_type = db.Column(db.String(20), default='text', nullable=False)  # text, image, video
    file_url = db.Column(db.String(500))  # 图片或视频的URL
    file_name = db.Column(db.String(200))  # 文件名
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    is_read = db.Column(db.Boolean, default=False)      # 未读/已读
    created_at = db.Column(db.DateTime, default=datetime.now)

    sender = db.relationship('User', foreign_keys=[sender_id])
    session = db.relationship('ChatSession', backref=db.backref('messages', lazy=True,cascade='all,delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'session_id':self.session_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else "未知用户",
            'sender_avatar': self.sender.avatar if self.sender else "",
            'content': self.content,
            'message_type': self.message_type,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# --- 7. 记录积分历史模型 (新增) ---
class PointsHistory(db.Model):
    __tablename__ = 'points_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_change = db.Column(db.Integer, nullable=False)  # 积分变化的数量
    action = db.Column(db.String(100), nullable=False)  # 积分变化的动作（如：购买服务、发布悬赏等）
    description = db.Column(db.String(255))  # 可选的描述字段，记录变动的具体原因
    created_at = db.Column(db.DateTime, default=datetime.now)  # 记录时间

    user = db.relationship('User', backref=db.backref('points_history', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'points_change': self.points_change,
            'action': self.action,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# --- 8. 浏览记录模型 (用于个性化推荐) ---
class ViewHistory(db.Model):
    __tablename__ = 'view_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref=db.backref('view_history', lazy=True))
    post = db.relationship('Post', backref=db.backref('view_history', lazy=True))
    
    # 防止重复记录（同一用户多次查看同一帖子只记录一次，更新查看时间）
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_view'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'viewed_at': self.viewed_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# --- 9. 收藏模型 (新增) ---
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref=db.backref('favorites', lazy=True))
    post = db.relationship('Post', backref=db.backref('favorites', lazy=True))
    
    # 防止重复收藏（同一用户不能重复收藏同一帖子）
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_favorite'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
