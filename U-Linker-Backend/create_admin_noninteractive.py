#!/usr/bin/env python3
"""
非交互式创建管理员账号脚本
使用方法：
python create_admin_noninteractive.py --username admin --password your_password --name "管理员" --college "学院" --student_id "学号"
"""

from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
import argparse
import sys

def create_admin_noninteractive(username, password, name=None, college=None, student_id=None):
    """非交互式创建管理员账号"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("创建管理员账号（非交互式）")
        print("=" * 60)
        
        if not username:
            print("❌ 用户名不能为空")
            return False
        
        if not password:
            print("❌ 密码不能为空")
            return False
        
        if len(password) < 8:
            print("❌ 密码长度不能小于8位")
            return False
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"⚠️  用户 '{username}' 已存在")
            choice = input("是否将其设置为管理员？(y/n): ").strip().lower()
            if choice == 'y':
                existing_user.is_admin = True
                db.session.commit()
                print(f"✅ 用户 '{username}' 已设置为管理员")
                return True
            else:
                print("❌ 操作已取消")
                return False
        
        # 使用提供的值或默认值
        name = name or username
        college = college or "管理员"
        student_id = student_id if student_id else None
        
        try:
            # 创建管理员用户
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                name=name,
                college=college,
                student_id=student_id,
                points=1000,  # 管理员默认1000积分
                is_admin=True
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("=" * 60)
            print("✅ 管理员账号创建成功！")
            print("=" * 60)
            print(f"用户名: {username}")
            print(f"姓名: {name}")
            print(f"学院: {college}")
            print(f"管理员权限: 是")
            print(f"初始积分: 1000")
            print("=" * 60)
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建失败: {str(e)}")
            return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='创建管理员账号（非交互式）')
    parser.add_argument('--username', required=True, help='管理员用户名')
    parser.add_argument('--password', required=True, help='管理员密码（至少8位）')
    parser.add_argument('--name', help='姓名（可选）')
    parser.add_argument('--college', help='学院（可选）')
    parser.add_argument('--student_id', help='学号（可选）')
    
    args = parser.parse_args()
    
    success = create_admin_noninteractive(
        username=args.username,
        password=args.password,
        name=args.name,
        college=args.college,
        student_id=args.student_id
    )
    
    sys.exit(0 if success else 1)

