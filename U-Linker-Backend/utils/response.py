from flask import jsonify

def success(data=None, message="操作成功"):
    """成功响应"""
    response = {
        "code": 200,
        "message": message,
        "data": data
    }
    return jsonify(response), 200

def error(message="操作失败", code=400):
    """错误响应"""
    response = {
        "code": code,
        "message": message,
        "data": None
    }
    return jsonify(response), code

