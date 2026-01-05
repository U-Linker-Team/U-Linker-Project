#!/usr/bin/env python3
"""
创建管理员账号脚本
使用方法：
1. 激活虚拟环境：source venv/bin/activate
2. 运行脚本：python3 create_admin.py
"""

from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    """创建管理员账号"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("创建管理员账号")
        print("=" * 60)
        
        # 获取输入
        username = input("请输入管理员用户名: ").strip()
        if not username:
            print("❌ 用户名不能为空")
            return
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"⚠️  用户 '{username}' 已存在")
            choice = input("是否将其设置为管理员？(y/n): ").strip().lower()
            if choice == 'y':
                existing_user.is_admin = True
                db.session.commit()
                print(f"✅ 用户 '{username}' 已设置为管理员")
                return
            else:
                print("❌ 操作已取消")
                return
        
        password = input("请输入密码: ").strip()
        if not password:
            print("❌ 密码不能为空")
            return
        
        if len(password) < 8:
            print("❌ 密码长度不能小于8位")
            return
        
        name = input("请输入姓名（可选，直接回车跳过）: ").strip() or username
        college = input("请输入学院（可选，直接回车跳过）: ").strip() or "管理员"
        student_id = input("请输入学号（可选，直接回车跳过）: ").strip() or ""
        
        try:
            # 创建管理员用户
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                name=name,
                college=college,
                student_id=student_id if student_id else None,
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
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建失败: {str(e)}")

if __name__ == '__main__':
    create_admin()

