import os
from flask import Blueprint, request, session
from utils.response import success, error
from extensions import db
from models import User,PointsHistory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import current_app, url_for
from sqlalchemy import or_
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# 1. 登录接口 (POST /auth/login)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return error(message="请提供用户名和密码")

    username = data.get('username')
    password = data.get('password')

    # 查找用户
    user = User.query.filter(
        or_(
            User.username == username, 
            User.student_id == username
        )
    ).first()

    # 检查锁定状态
    if user and user.lockout_until:
        if datetime.now() < user.lockout_until:
            wait_seconds = (user.lockout_until - datetime.now()).seconds
            wait_minutes = wait_seconds // 60 + 1
            return error(message=f"账号已被锁定,请在{wait_minutes}分钟后重试")
        else:
            # 解锁
            user.lockout_until = None
            user.failed_login_attempts = 0
            db.session.commit()

    # 验证密码
    if user and check_password_hash(user.password_hash, password):
        # 检查是否被封禁
        if user.ban_until and user.ban_until > datetime.now():
            ban_until_str = user.ban_until.strftime('%Y-%m-%d %H:%M:%S')
            return error(message=f"您的账号已被封禁至 {ban_until_str}，无法登录")
        
        # 密码正确
        user.failed_login_attempts = 0
        user.lockout_until = None
        user.last_login = datetime.now()  # 更新最后登录时间
        db.session.commit()

        #将用户ID存入服务器端的Session
        session.permanent = True  # 设置为持久化，防止关闭浏览器就退出
        session['user_id'] = user.id
        
        result_data = {
            "token": "session-active",
            "user": user.to_dict()
        }
        return success(data=result_data, message="登录成功")
    else:
        # 密码错误或用户不存在
        if user:
            current_attempts = user.failed_login_attempts if user.failed_login_attempts else 0
            user.failed_login_attempts = current_attempts + 1

            if user.failed_login_attempts >= 5:
                user.lockout_until = datetime.now() + timedelta(minutes=15)
                db.session.commit()
                return error(message="连续登录失败5次,账号已被锁定15分钟")
            else:
                remaining = 5 - user.failed_login_attempts
                db.session.commit()
                return error(message=f"用户名或密码错误，您还有 {remaining} 次尝试机会")
        else:
            return error(message="用户名或密码错误")


# 2. 注册接口 (POST /auth/register)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    # 默认字段
    name = data.get('name', username)
    college = data.get('college', '未知学院')
    student_id = data.get('studentId', '')
    points = data.get('points', 100)  # 默认赠送100积分
    avatar = data.get('avatar', '')

    if not username or not password:
        return error(message="账号密码不能为空")

    if password != confirm_password:
        return error(message="两次输入的密码不一致")

    if len(password) < 8:
        return error(message="密码长度不能小于8")

    # 密码强度检查
    has_digit = any(char.isdigit() for char in password)
    has_alpha = any(char.isalpha() for char in password)

    if not (has_digit and has_alpha):
        return error(message="输入密码必须同时包含字母和数字")

    # 检查重复
    existing_user = User.query.filter(or_(User.username == username, User.student_id == student_id)).first()
    if existing_user:
        if existing_user.username == username:
            return error(message="该用户名已经被注册")
        else:
            return error(message="该学号已经被使用")

    try:
        hashed_pw = generate_password_hash(password)
        new_user = User(
            username=username,
            password_hash=hashed_pw,
            name=name,
            college=college,
            student_id=student_id,
            points=points,
            avatar=avatar
        )
        db.session.add(new_user)

        db.session.flush() 
        # --- 新增积分历史记录 ---
        history = PointsHistory(
            user_id=new_user.id,
            points_change=points,
            action="新用户注册",
            description="欢迎来到 U-Linker,新用户注册奖励 100 积分"
        )
        db.session.add(history)
        
        db.session.commit()

        return success(message="注册成功, 赠送100积分")

    except Exception as e:
        db.session.rollback()
        print(f"Database Error: {e}")
        return error(message="注册失败, 请稍后再试")


# 3. 登出功能 (GET /auth/logout)
@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return success(data={"redirect": "/login"}, message="登出成功")


# 4. 获得个人信息 (GET /auth/profile)
# 修改点：支持通过 ?user_id=xxx 查询指定用户
@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    # 获取 URL 参数 user_id
    user_id = request.args.get('user_id')

    if not user_id:
        return error(message="请提供 user_id 参数")

    # 在数据库中查找
    user = db.session.get(User, user_id)

    if user:
        return success(data=user.to_dict())
    else:
        return error(message="用户不存在")

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/update_profile', methods=['POST'])
def update_profile():
    # 1. 获取当前用户 (通过 user_id 参数，或者你可以改成从 token 获取)
    # 为了方便测试，我们暂时用 form-data 传 user_id
    user_id = request.form.get('user_id')
    if not user_id:
        return error(message="未登录或缺少 user_id")
    
    user = db.session.get(User, user_id)
    if not user:
        return error(message="用户不存在")

    try:
        # 2. 修改普通资料 (如果有传的话)
        new_name = request.form.get('name')
        if new_name:
            user.name = new_name
            
        # 3. 处理头像上传 (核心逻辑)
        if 'avatar' in request.files:
            file = request.files['avatar']
            
            # 检查文件是否存在且格式合法
            if file and allowed_file(file.filename):
                # 为了防止文件名冲突，重命名为: user_id_时间戳.jpg
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"user_{user.id}_{int(datetime.now().timestamp())}.{ext}")
                
                # 拼接保存路径: 项目根目录/static/avatars/文件名
                # 注意：Flask 默认把 static 文件夹作为静态资源目录
                save_dir = os.path.join(current_app.root_path, 'static', 'avatars')
                
                # 如果目录不存在，自动创建 (双重保险)
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                    
                file_path = os.path.join(save_dir, filename)
                file.save(file_path)
                
                # 4. 更新数据库里的路径 (存的是 URL 路径)
                # 这样前端可以直接访问 http://localhost:5000/static/avatars/xxx.jpg
                user.avatar = url_for('static', filename=f'avatars/{filename}')

        db.session.commit()
        return success(message="个人资料修改成功", data=user.to_dict())

    except Exception as e:
        db.session.rollback()
        print(f"Update Error: {e}")
        return error(message="修改失败，请重试")