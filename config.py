import os
from datetime import timedelta
##数据库链接配置
#SQLALCHEMY_DATABASE_URI = 'mysql://root:SQL123@localhost:3306/test' #之前项目的连接方式,下面是一种更明白的方式
#下面这些属性在Workbench上都可以看到(密码要自己记住)
DB_USERNAME = 'root'
DB_PASSWORD = 'SQL123'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'
DB_NAME = 'pythonbbs' #数据库名字
DB_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %(DB_USERNAME,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONSl = False #是否需要发出跟踪修改的信号，这里选否
################

##邮箱配置
#qijnxgdhlzzabejh pop3服务密码
#MAIL_USE_TLS:端口号587
#MAIL_USE_SSL:端口号465
#邮箱服务器是QQ邮箱
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 587 #/465
MAIL_USE_TLS = True
#MAIL_USE_SSL = True #TSL/SSL二选一
MAIL_USERNAME = "1045109874@qq.com"
MAIL_PASSWORD = "qijnxgdhlzzabejh"
MAIL_DEFAULT_SENDER = "1045109874@qq.com"

#Celery的redis配置  本次开发broker何backend都采用redies
CELERY_BROKER_URL= "redis://127.0.0.1:6379/0"  #6379是安装redis默认的端口号
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

#Flask-caching配置缓存，使用redis
CACHE_TYPE = "RedisCache"
CACHE_DEFAULT_TIMEOUT = 300 #设置过期时间为300秒
CACHE_REDIS_HOST = "127.0.0.1" #主机名
CACHE_REDIS_PORT = 6379 #端口号

#邮件验证码发送按钮的Ajax请求相关,csrf token需要一个SECRET_KEY
SECRET_KEY = "ssdfasdf"
############

#图形验证码配置，字体文件需要获取项目根路径
BASE_DIR = os.path.dirname(__file__)#获取当前路径

#session.permanent =True情况下的过期时间
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

#头像配置
AVATARS_SAVE_PATH = os.path.join(BASE_DIR,"media","avatars")

#帖子图片存放路径 富文本编辑器采用wangEditor的V4版本 #https://www.wangeditor.com/v4/pages/01-%E5%BC%80%E5%A7%8B%E4%BD%BF%E7%94%A8/01-%E5%9F%BA%E6%9C%AC%E4%BD%BF%E7%94%A8.html
POST_IMAGE_SAVE_PATH = os.path.join(BASE_DIR,"media","post")

#配置每一页帖子展示的数量
PER_PAGE_COUNT=10

#设置jwt_token过期时间
JWT_ACCESS_TOKEN_EXPIRES= timedelta(days=50)

#轮播图存放路径
BANNER_IMAGE_SAVE_PATH = os.path.join(BASE_DIR,"media","banner")

