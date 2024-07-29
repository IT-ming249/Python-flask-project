from flask import g,redirect,url_for
from functools import wraps
#用于存放所有装饰器


#要求登录的装饰器
def login_required(func):
    @wraps(func) #保留输入函数的原参数信息
    def inner(*args,**kwargs):
        if hasattr(g,"user"):
            #g中有user这个属性说明登录了
            return func(*args,**kwargs)
        else:
            #未登录则返回登录页面
            return redirect(url_for("front.login"))
    return inner

