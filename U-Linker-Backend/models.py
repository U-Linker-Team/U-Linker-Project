from extensions import db
from datetime import datetime

# --- 1. 用户模型 ---
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(50))
    college = db.Column(db.String(50))
    student_id = db.Column(db.String(20), unique=True)
    points = db.Column(db.Integer, default=100)
    avatar = db.Column(db.String(200))
    failed_login_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'points': self.points,
            'avatar': self.avatar
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
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# --- 3. 申请记录模型 ---
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

    post = db.relationship('Post', backref=db.backref('applications', lazy=True))
    applicant = db.relationship('User', backref=db.backref('my_applications', lazy=True))


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
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# --- 5. 记录积分历史模型  ---
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



