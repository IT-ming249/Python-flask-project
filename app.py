from flask import Flask
import config
from exts import db,mail,cache,csrf,avatar,jwt,cors
from flask_migrate import Migrate
from models import auth
from apps.front import front_bp
from apps.media import media_bp
from apps.cmsapi import cmsapi_bp
from bbscelery import make_celery
import commands





app = Flask(__name__)
app.config.from_object(config)#应用配置项，这属于输入部的连接
#######下面的操作按照项目开发的时间顺序来写
#数据库链接相关
db.init_app(app)#SQLAlchemy与app进行绑定
migrate = Migrate(app,db)#将应用对象和数据库对象传递给Migrate对象，以便进行数据库迁移操作, 对db做出调整时需要重新在终端中migrate和upgrade一下
'''将ORM模型映射到数据库三部曲
1.初始化迁移仓库：flask db init
2.将orm模型生成迁移脚本：flask db migrate
3.运行迁移脚本，生成表：flask db upgrade'''
######邮件功能相关#######
mail.init_app(app)
mycelery = make_celery(app)
'''python中操作redis要安装两个包
1. pip install redis
2. pip install hiredis
在windows上使用celery需要借助gevent
pip install gevent 
终端运行代码
celery -A app.mycelery worker --loglevel=info -P gevent     mycelery是自己定义的celery对象名
'''

#注册前台蓝图
app.register_blueprint(front_bp)

#发送功能完成
#接下来是缓存以便验证
cache.init_app(app)
#邮件验证码发送按钮的Ajax请求相关
csrf.init_app(app)
######邮件功能相关#######
#头像相关
avatar.init_app(app)
app.register_blueprint(media_bp) #注册图片相关的蓝图

#注册命令
app.cli.command("init_boards")(commands.init_boards)
app.cli.command("create_test_posts")(commands.create_test_posts)
app.cli.command("init_roles")(commands.init_roles)
app.cli.command("bind_roles")(commands.bind_roles)

#初始化jwt  jwt参考文档：https://www.zlkt.net/post/detail/60
jwt.init_app(app)
#注册comsapi相关的蓝图
app.register_blueprint(cmsapi_bp)

#cors跨域访问
cors.init_app(app,resources={r"/cmsapi/*": {"origins": "*"}})#所有以/cmsapi开头的路由都允许跨域访问，origins表示访问来源

#排除cmsapi的csrf验证
csrf.exempt(cmsapi_bp)

##部署
#pip freeze -> requirements.txt  将所有依赖项打包到 requirements.exe中
#git init 生产空的git仓库

#vue参考文档：https://www.zlkt.net/book/detail/13
if __name__ == '__main__':
    app.run()
