rom flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db
from routes.auth import auth_bp
from routes.market import market_bp
from routes.transaction import transaction_bp
from routes.recommendation import recommendation_bp
from routes.chat import chat_bp
from routes.admin import admin_bp  # 管理员路由
from routes.debug import debug_bp  # 调试路由
import os
from datetime import timedelta
from sqlalchemy import text


def create_app():
    # 禁用 Flask 默认的 static 路由，使用自定义路由
    app = Flask(__name__, static_folder=None, static_url_path=None)
    
    # 从环境变量读取配置，如果没有则使用默认值
    # 数据库配置：优先使用环境变量 DATABASE_URL，否则使用 MySQL 或 SQLite
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # 如果没有环境变量，尝试使用 MySQL 配置
        mysql_user = os.getenv('MYSQL_USER')
        mysql_password = os.getenv('MYSQL_PASSWORD')
        mysql_database = os.getenv('MYSQL_DATABASE')
        mysql_host = os.getenv('MYSQL_HOST', 'mysql')  # 使用服务名'mysql'
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        
        if mysql_user and mysql_password and mysql_database:
            app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}'
        else:
            # 开发环境默认使用 SQLite
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///u-linker.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'u-linker-secret')  # 从环境变量读取，默认值仅用于开发
    # 上传文件配置
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # 确保 uploads 文件夹存在
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Session 配置
    flask_env = os.getenv('FLASK_ENV', 'development')
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 使用代理后，同源请求可以使用 Lax
    app.config['SESSION_COOKIE_SECURE'] = False  # HTTP 环境下必须设为 False，否则浏览器会丢弃 Cookie
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_DOMAIN'] = None  # 不限制域名
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session 有效期：7天

    # Nginx 代理适配：让 Flask 能正确识别代理后的请求
    # 这样 Flask 才能正确生成 URL 和获取真实 IP
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    db.init_app(app)

    # CORS 配置：从环境变量读取允许的源，如果没有则使用默认值
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://localhost:5173,http://localhost:5174,http://127.0.0.1:8000,http://127.0.0.1:5173,http://127.0.0.1:5174,http://121.89.81.18,http://121.89.81.18:80')
    # 将字符串分割为列表
    origins_list = [origin.strip() for origin in cors_origins.split(',')]
    
    CORS(app, 
         resources={r"/*": {"origins": origins_list}},
         supports_credentials=True)
    
    # 注册路由
    app.register_blueprint(auth_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)  # 管理员路由
    app.register_blueprint(recommendation_bp)  # 推荐系统路由
    app.register_blueprint(debug_bp)  # 调试路由
    
    # ========== 健康检查路由 ==========
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查端点：检查服务和数据库连接状态"""
        try:
            # 测试数据库连接
            db.session.execute(text('SELECT 1'))
            database_status = "connected"
        except Exception as e:
            database_status = f"disconnected: {str(e)}"
        
        return jsonify({
            "status": "ok",
            "service": "backend",
            "database": database_status
        }), 200
    
    # ========== 静态文件服务路由 ==========
    # 提供 uploads 文件夹的静态文件服务
    # 这样前端可以通过 /uploads/filename 访问上传的图片
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """提供上传文件的访问服务"""
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            filename
        )
    
    # 提供 static 文件夹的静态文件服务（头像等）
    # 这样前端可以通过 /static/avatars/filename 访问头像
    @app.route('/static/<path:filename>')
    def static_file(filename):
        """提供静态文件的访问服务（头像等）"""
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            filename
        )

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)
