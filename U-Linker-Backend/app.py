from flask import Flask
from flask_cors import CORS
from extensions import db
from routes.auth import auth_bp
from routes.market import market_bp
from routes.transaction import transaction_bp
from routes.chat import chat_bp  # <--- 新增导入


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///u-linker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'u-linker-secret'

    db.init_app(app)

    # 如果不知道前端端口，可以用列表写多个，或者用正则
    CORS(app, 
         resources={r"/*": {"origins": ["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:8000","http://127.0.0.1:5173"]}},
         supports_credentials=True)
    
    # 注册路由
    app.register_blueprint(auth_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(chat_bp)  # <--- 新增注册

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8000)
