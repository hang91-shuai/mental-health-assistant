"""
统一 API 返回格式 — 所有接口调用此模块构造响应
"""

from flask import jsonify


def success(data=None, message="success"):
    """成功响应"""
    return jsonify({
        "code": 200,
        "message": message,
        "data": data if data is not None else {}
    })


def error(message="服务器内部错误", code=500, data=None):
    """错误响应"""
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    }), code


def bad_request(message="请求参数错误"):
    """400 快捷方法"""
    return error(message, code=400)


def not_found(message="资源未找到"):
    """404 快捷方法"""
    return error(message, code=404)
