from flask import Blueprint, request, render_template, jsonify, current_app,make_response,session,redirect,g,jsonify,url_for
import string
import random
from exts import mail
from flask_mail import Message
from exts import cache,db,avatar
from utils import restful
from utils.captcha import Captcha
import time
from hashlib import md5
from io import BytesIO
from .forms import RegisterForm,LoginForm, UploadImageForm, EditProfileForm, PublicPostForm,PublicCommentForm
from models.auth import UserModel,Permission
from models.post import PostModel,BoardModel,BannerModel,CommentModel
from .decorators import login_required
from flask_avatars import Identicon
from flask_paginate import get_page_parameter,Pagination
from sqlalchemy.sql import func
from flask_jwt_extended import create_access_token
import os


#ctel+鼠标左键点击可进入函数内部查看
#通过创建蓝图对象，可以将相关的路由、视图函数和静态文件等组织在一起，以便更好地管理和组织Flask应用程序的功能模块
bp = Blueprint("front",__name__,url_prefix="/") #front是蓝图名称

#####################首页#############################
@bp.route('/')
def index():
    # 根据不同方式排序
    sort = request.args.get("st", type=int, default=1)  # 指定排序方式序号st
    #板块过滤
    boards =BoardModel.query.order_by(BoardModel.priority.desc()).all() #板块名称按优先级从大到小排序
    board_id = request.args.get("bd",type=int,default=None)

    #实现帖子分页
    # flask-paginate参考文档 https://flask-paginate.readthedocs.io/en/master/
    # posts = PostModel.query.order_by(PostModel.create_time.desc()).all()#要分页就不能一次性获取所有帖子
    post_qurey = None

    if sort == 1:
        #按创建时间排序
        post_qurey = PostModel.query.order_by(PostModel.create_time.desc())
    elif sort == 2:
        #按评论数排序涉及到跨表查询
        #将Post和Comment表进行左外连接，并根据post_id进行分组，再更具评论comment_id的数量从大到小进行排序,如果评论数量相同就按照时间排序
        post_qurey=db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id).order_by(func.count(CommentModel.id).desc(),PostModel.create_time.desc())
    #分页功能的切片头尾
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # p1:0-9 p2:10-19
    start = (page - 1) * current_app.config['PER_PAGE_COUNT']
    end = start + current_app.config['PER_PAGE_COUNT']

    if board_id:
        #有板块id则按照板块id进行过滤
        #当按照评论最多查询时，只让它从postmodel中寻找就可以了，因为sort=2连接了两张表,flask两张表都查，会导致comment表中找不到board_id
        post_qurey=post_qurey.filter(PostModel.board_id==board_id)

    total = post_qurey.count()  # 帖子的总数，Pagination需要传入此参数
    posts = post_qurey.slice(start, end)  # 帖子数量，已切片
    pagination= Pagination(bs_version=3,page=page,total=total,prev_label='上一页',next_label='下一页')

    banners=BannerModel.query.order_by(BannerModel.priority.desc()).all() #获取轮播图数据
    content ={
        "boards":boards,
        "posts":posts,
        #分页
        "pagination":pagination,
        #排序
        "st":sort,
        #分板块
        "bd":board_id,
        #轮播图
        "banners":banners
    }
    return render_template("front/index.html", **content)

#钩子函数：before_request。 在调用front蓝图下的视图函数之前，都会先执行钩子函数
@bp.before_request
def front_before_request():
    if 'user_id' in session:
        user_id = session.get("user_id")#若用户已登录则从session中获取用户id
        user = UserModel.query.get(user_id) #主键可以用get获取
        setattr(g,"user",user) #给user这个全局对象设置一个属性，名为“user”,值为从数据库里获得的user

#请求 => 执行before_request => 若视图函数返回模板 => 执行context_processor => 将context_processor返回的变量也添加到模板中

#上下文处理器
@bp.context_processor
def front_context_processor():
    if hasattr(g,"user"): #检查g中有没有user这个属性
        return {"user": g.user}  #此时这个user已经被渲染到前端的所有的html模板中了
    else:
        return {}

#后台管理页面接口
@bp.get("/cms")
def cms():
    return render_template("cms/index.html")


#####################首页#############################


#####################发布帖子页面#############################
@bp.route("/post/public",methods=['GET', 'POST']) #发布帖子可能使用get/post方法
@login_required
def public_post():
    if request.method == "GET":
        boards = BoardModel.query.order_by(BoardModel.priority.desc()).all()
        return render_template("front/public_post.html",boards=boards)
    else:
        form = PublicPostForm(request.form)
        if form.validate():
            tittle = form.tittle.data
            content = form.content.data
            board_id = form.board_id.data
            try:
                #get 方法：接收一个id作为参数，如果找到了，会返回这条数据
                #如果没找到就抛出异常
                board = BoardModel.query.get(board_id)
            except Exception as e:
                return restful.params_error(message='板块不存在')
            post_model = PostModel(tittle=tittle,content=content,board=board,author=g.user)
            db.session.add(post_model)
            db.session.commit()
            return restful.ok(data={"id":post_model.id})#发布帖子成功后返回帖子id以便跳转到帖子详情页
        else:
            message = form.messages[0]  # 每次只返回第一条错误信息
            return restful.params_error(message=message)



#富文本编辑器上传图片
@bp.post("/post/image/upload")
@login_required
def upload_post_image():
    form = UploadImageForm(request.files) #头像在request.files中
    if form.validate():
        image = form.image.data
        #filename =  image.filename  #不使用用户上传上来的文件名，以防黑客攻击
        filename = image.filename  #form.image.data.filename获取文件名
        _, ext=os.path.splitext(filename) #ext为后缀
        filename =md5((g.user.email+str(time.time())).encode("utf-8")).hexdigest()+ext
        image_path= os.path.join(current_app.config['POST_IMAGE_SAVE_PATH'],filename)
        image.save(image_path) #将头像保存到media文件夹中
        g.user.avatar=filename #将头像保存到数据库中，由于个人设置是在登录以后才能进入，所以这里可以用全局变量g
        db.session.commit()
        return jsonify({
            "errno":0,
            "data":[{
                "url":url_for("media.get_post_image",filename=filename),
                "alt":filename,
                "href":""
            }]})
    else:
        message = form.messages[0]  # 每次只返回第一条错误信息
        return restful.params_error(message=message)

#####################发布帖子页面#############################


#####################帖子详情页面#############################
@bp.get("/post/detail/<int:post_id>")
def post_detail(post_id):
    try:
        post_model = PostModel.query.get(post_id)
    except:
        return "404"
    #获取评论数量
    comment_count =CommentModel.query.filter_by(post_id=post_id).count()
    context = {
        "post":post_model,
        "comment_count":comment_count
    }
    return render_template("front/post_detail.html",**context)
    #return render_template("front/post_detail.html",post=post_model,comment_count=comment_count) 等价于上面那行代码

#评论功能
@bp.post("/comment")
@login_required
def public_comment():
    form = PublicCommentForm(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        try:
            post_model =PostModel.query.get(post_id)
        except Exception as e:
            return restful.params_error(message='帖子不存在')
        comment = CommentModel(content=content,post_id=post_id,author_id=g.user.id)
        db.session.add(comment)
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(message=form.messages[0])
#####################帖子详情页面#############################


#############登录页面###############
@bp.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("front/login.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data #这里过来的是用户输入的明文密码
            remember = form.remember.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                return restful.params_error("邮箱或密码错误")
            if not user.check_password(password):
                return restful.params_error("密码错误")
            #运行到此表示验证通过，可登录
            session['user_id']=user.id  #session['user_id']将user_id加密后存入cookie中
            #接下来生成jwt_token以便跨服务器验证，适用于前后端分离项目
            token=""
            permissions=[] #获取用户拥有的权限
            if user.is_staff:
                token=create_access_token(identity=user.id)#如果是员工才生成jwt_token
                #dir(Permission)输出包括自定义的属性和python原本内置的属性  ['ALL_PERMISSION', 'BANNER', 'COMMENT', 'POST', 'STAFF', 'USER', 'VISITOR', '__class__', '__delattr__'......]
                for per in dir(Permission):
                    if not per.startswith("_"): #不以_开头的都是自定义的权限
                        permission=getattr(Permission,per) #取出其中一个权限的值
                        if user.has_permission(permission):
                            permissions.append(per.lower())
            if remember == 1:
                #默认session过期时间，就是浏览器关闭了就会过期
                session.permanent =True #勾选了记住则延后session的过期时间，过期时间需要在config中配置

            user_dict=user.to_dict()
            user_dict['permissions']=permissions

            return restful.ok(data={"token":token, "user":user_dict}) #SerizlizerMixin会给ORM模型添加一个to_dict方法  user.to_dict()返回的信息会包括与user相关的引用的信息，会造成资源浪费
        else:
            return restful.params_error(message=form.messages[0])

##退出登录视图
@bp.route("/logout")
def logout():
    session.clear() #将登录状态写入的session清空
    return redirect("/")

#############登录页面###############


######################注册页面########################
@bp.route("/register", methods=['GET','POST'])
def register():
    if request.method == "GET":
        return render_template("front/register.html")
    else:
        form = RegisterForm(request.form)
        if form.validate(): #若用户注册信息通过了验证表单
            email = form.email.data
            username = form.username.data
            password = form.password.data
            #标识生成法生成头像
            identicon = Identicon() #创建 Identicon 类的实例
            fileames = identicon.generate(text=md5(email.encode("utf-8")).hexdigest()) #直接用加密后的邮箱作为头像名称
            avatar = fileames[2] #这是头像尺寸，详见参考文档https://zlkt.net/post/detail/59
            user = UserModel(email=email,username=username,password=password,avatar=avatar)
            db.session.add(user)
            db.session.commit()
            return restful.ok()
        else:
            # form.errors中存放了所有的错误信息
            #print(form.errors)
            #return "failure"
            message = form.messages[0]#每次只返回第一条错误信息
            return restful.params_error(message=message)


#########邮箱视图
'''@bp.get('/email/captcha') #等价@bp.route('email/captcha', methods=['GET'])
def email_captcha():
    #链接使用 /emial/captcha?email=xx@qq.com
    email = request.args.get("email") #获取邮箱
    if not email:
        return jsonify({"code":400,"msessage":"请输入邮箱账号"})

    # 产生随机六位数字验证码
    source = list(string.digits)
    captcha = "".join(random.sample(source,6))#source列表中随机取6为作为验证码，是字符串
    message = Message(subject="注册验证码",recipients=[email],body="您的注册验证码为：%s"%captcha)
    #subject为邮件主题，recipients为接收者（数据类型为列表），body就是邮件内容
    try:
        # 发送邮件实际上是一个网络请求,需要响应时间，可以使用celery将该请求放入一个独立于网站的任务队列中
        mail.send((message))#有可能会失败
    except Exception as e:
        print("邮件发送失败")
        print(e) #打印错误信息
        return jsonify({"code":500,"msessage":"邮件发送失败"})
    return jsonify({"code":200,"msessage":"邮件发送成功"}) #这是基础版'''

#celery实现异步发送邮件  参考文档：https://zlkt.net/post/detail/56
@bp.get('/email/captcha') #等价@bp.route('email/captcha', methods=['GET'])
def email_captcha():
    #链接使用 /emialcaptcha?email=xx@qq.com
    email = request.args.get("email") #获取邮箱,查询字符串传参
    if not email:
        return restful.params_error(message="请先传入邮箱")#这是参数错误
        #return jsonify({"code":400,"msessage":"请输入邮箱账号"})
    # 产生随机六位数字验证码
    source = list(string.digits)
    captcha = "".join(random.sample(source,6))#验证码，是字符串
    subject = "注册验证码"
    body = "您的注册验证码为：%s" % captcha
    #subject为邮件主题，recipients为接收者（数据类型为列表），body就是邮件内容
    current_app.celery.send_task("send_mail", (email,subject,body))
    # app已经通过app.celery与app绑定,故可以使用current_app直接指向当前app项目
    #到此验证码发送完成

    #为了后续验证用户输入的验证码是否正确，需要将发送的验证码存入cache中，以便后续拿出来比对
    #配置flask-caching  参考文档：https://zlkt.net/post/detail /58
    cache.set(email,captcha) #email是作为键，captcha是对应的值
    print(cache.get(email)) #打印一下缓存的验证码看看有没有缓存成功
    return restful.ok(message="邮件发送成功")
    #return jsonify({"code":200,"msessage":"邮件发送成功"})

#在注册页中集成图像验证码
@bp.route("/graph/captcha")
def graph_captcha():
    captcha, image = Captcha.gene_graph_captcha() #Captcha类方法返回的是验证码的文字以及图片
    #将验证码存入缓存
    key = md5((captcha+str(time.time())).encode('utf-8')).hexdigest() #cache中验证码的键,图像验证码没有像email这样的键，需要生成一个
    cache.set(key,captcha) #以captcha验证码为cache中的值
    #将验证码缓存到内存中
    out = BytesIO()
    image.save(out,"png") #image是Image类，浏览器识别不来，使用save方法将其转换为二进制数据
    out.seek(0)#将out的文件指针指向最开始的位置
    resp = make_response(out.read())#读取out中的数据作为响应
    resp.content_type = "image/png" #规定响应的类型为图片
    #将验证码对应的key存到cookie中，以便后续分辨该验证码是不是属于正在注册的用户，浏览器从cookie中取得键，再从cache中取得验证码
    resp.set_cookie("_graph_captcha_key",key,max_age=3600)#max_age=3600为失效时间
    return resp
######################注册页面########################



###################个人设置页#############################
@bp.route("/setting")
@login_required  #setting()函数作为login_required装饰器的输入
def setting():
    #适用flask-avatars解决头像问题 参考文档：https://zlkt.net/post/detail/59
    #生成默认头像方法一：gravatars生成头像，方法二在media.view中
    email_hash = md5(g.user.email.encode("utf-8")).hexdigest() #setting模板需要一个md5加密的邮箱地址
    return render_template("front/setting.html",email_hash=email_hash)

#用户自己上传头像
@bp.post("/avatar/upload")
@login_required
def upload_avatar():
    form = UploadImageForm(request.files) #头像在request.files中
    if form.validate():
        image = form.image.data
        #filename =  image.filename  #不使用用户上传上来的文件名，以防黑客攻击
        filename = image.filename
        _, ext=os.path.splitext(filename) #ext为后缀
        filename =md5((g.user.email+str(time.time())).encode("utf-8")).hexdigest()+ext
        image_path= os.path.join(current_app.config['AVATARS_SAVE_PATH'],filename)
        image.save(image_path)
        g.user.avatar = filename
        db.session.commit()
        return restful.ok(data={"avatar": filename})
    else:
        message = form.messages[0]  # 每次只返回第一条错误信息
        return restful.params_error(message=message)

#用户个性签名
@bp.post("/profile/edit")
@login_required
def edit_profile():
    form =EditProfileForm(request.form)
    if form.validate():
        signature = form.signature.data
        g.user.signature = signature
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(message=form.messages[0])
###################个人设置页#############################

