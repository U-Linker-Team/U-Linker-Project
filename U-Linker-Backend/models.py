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




