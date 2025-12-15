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





