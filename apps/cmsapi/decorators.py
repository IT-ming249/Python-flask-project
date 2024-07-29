from functools import wraps
from flask import g
from utils import restful



def permission_required(permission): #这是接收参数的装饰器，比不接收参数的装饰器多了这一层，之前的login_required就是不接收参数的装饰器
    def outter(func):
        @wraps(func)
        def inner(*args,**kwargs):
            user = getattr(g,"user")
            if not user:
                return restful.unlogin_error()
            if user.has_permission(permission):
                return func(*args,**kwargs)  #用户登录了又有权限就正常执行视图函数
            else:
                return restful.permission_error(message="没有访问该接口的权限")
        return inner
    return outter
