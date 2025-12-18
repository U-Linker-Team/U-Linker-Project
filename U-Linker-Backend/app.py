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

    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)

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
