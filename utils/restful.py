# Restful API (可在以后的项目中复用)
# 面向开发者统一返回的数据格式
from flask import jsonify

class HttpCode(object):
    #响应正常
    ok = 200
    #没有登录的错误
    unloginerror = 401
    #没有权限的错误
    permissionerror = 403
    #客户端参数错误
    paramserror = 400
    #服务器错误
    servererror = 500

def _restful_result(code,message,data):
    return jsonify({"message":message or "","data":data or {},"code":code}) #message,data 可以没有值，但这个key要有

def ok(message = None,data =None):
    return _restful_result(code=HttpCode.ok,message=message,data=data)

def unlogin_error(message="未登录！"):
    return _restful_result(code=HttpCode.unloginerror,message=message,data=None)

def permission_error(message="没有访问权限！"):
    return _restful_result(code=HttpCode.permissionerror,message=message,data=None)

def params_error(message="参数错误!"):
    return _restful_result(code=HttpCode.paramserror,message=message,data=None)

def server_error(message="服务器开了个小差"):
    return _restful_result(code=HttpCode.servererror,message=message,data=None)
