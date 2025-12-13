from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 初始化配置
app = Flask(__name__)
# 允许跨域（方便前端Vue访问）
CORS(app)

# 数据库配置 (这里暂时用SQLite代替，方便演示，以后换MySQL只需要改这一行)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ulinker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 定义一个简单的示例模型 (Model) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# --- 简单的测试接口 ---
@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({
        "status": "success",
        "message": "Hello from Flask Backend! (U-Linker)"
    })

if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
    # 启动应用
    app.run(debug=True, port=5000)