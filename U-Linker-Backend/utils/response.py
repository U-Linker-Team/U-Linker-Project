#核心作用: 统一api响应格式 (处理前端对数据要求的苛刻)
from flask import jsonify
def success(data=None, message="操作成功"):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    })

def error(message="操作失败"):
    return jsonify({
        "status":"error",
        "message": message,
        "data": None
    })
