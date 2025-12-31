from flask import Flask, send_from_directory
from flask_cors import CORS
from extensions import db
from routes.auth import auth_bp
from routes.market import market_bp
from routes.transaction import transaction_bp
from routes.recommendation import recommendation_bp
from routes.chat import chat_bp
from routes.admin import admin_bp  # 管理员路由
import os


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///u-linker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'u-linker-secret'
    # 上传文件配置
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # 确保 uploads 文件夹存在
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Session 配置 - 使用代理后，请求是同源的，可以使用 'Lax'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 使用代理后，同源请求可以使用 Lax
    app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为 False，生产环境应设为 True（需要 HTTPS）
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_DOMAIN'] = None  # 不限制域名

    db.init_app(app)

    # 如果不知道前端端口，可以用列表写多个，或者用正则
    CORS(app, 
         resources={r"/*": {"origins": [
             "http://localhost:8080", 
             "http://localhost:5173", 
             "http://localhost:5174",
             "http://127.0.0.1:8000",
             "http://127.0.0.1:5173",
             "http://127.0.0.1:5174"
         ]}},
         supports_credentials=True)
    
    # 注册路由
    app.register_blueprint(auth_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)  # 管理员路由
    app.register_blueprint(recommendation_bp)  # 推荐系统路由
    
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

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)