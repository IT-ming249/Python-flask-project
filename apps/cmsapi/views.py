from flask import Blueprint,request,current_app,g
from utils import restful
from flask_jwt_extended import jwt_required,get_jwt_identity
from .forms import UploadImageForm,AddBannerForm,EditBannerForm
from models.auth import UserModel,Permission
from models.post import BannerModel,PostModel,CommentModel,BoardModel
from exts import db
from hashlib import md5
from sqlalchemy import func
import time
from datetime import datetime,timedelta
from .decorators import permission_required
import os


bp = Blueprint("cmsapi",__name__,url_prefix="/cmsapi")

@bp.before_request
@jwt_required()
def comsaip_before_request():
    if request.method =='OPTIONS':
        return
    identity  = get_jwt_identity()
    user = UserModel.query.filter_by(id=identity).first()
    if user:
        setattr(g,"user",user)



@bp.get("/")
@jwt_required()
def mytest():
    identity = get_jwt_identity() #获取的是create_access_token 传入的identity，当初传入的是user.id
    return restful.ok(message="success",data={"identity":identity})

############轮播图管理页面##########################
#轮播图上传
@bp.post("/banner/image/upload")
@permission_required(Permission.BANNER)
def upload_banner_image():
    form = UploadImageForm(request.files)  # 头像在request.files中
    if form.validate():
        image = form.image.data
        # filename =  image.filename  #不使用用户上传上来的文件名，以防黑客攻击
        filename = image.filename
        _, ext = os.path.splitext(filename)  # ext为后缀
        filename = md5((g.user.email + str(time.time())).encode("utf-8")).hexdigest() + ext
        image_path = os.path.join(current_app.config['BANNER_IMAGE_SAVE_PATH'], filename)
        print(image_path)
        image.save(image_path)
        return restful.ok(data={"image_url": filename})
    else:
        message = form.messages[0]  # 每次只返回第一条错误信息
        return restful.params_error(message=message)
#轮播图添加
@bp.post("/banner/add")
@permission_required(Permission.BANNER)
def add_banner():
    form = AddBannerForm(request.form)
    if form.validate():
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner_model = BannerModel(name=name,image_url=image_url,link_url=link_url,priority=priority)
        db.session.add(banner_model)
        db.session.commit()
        return restful.ok(data=banner_model.to_dict())
    else:
        message = form.messages[0]  # 每次只返回第一条错误信息
        return restful.params_error(message=message)

#获取轮播图列表
@bp.get("/banner/list")
@permission_required(Permission.BANNER)
def banner_list():
    banners=BannerModel.query.order_by(BannerModel.create_time.desc()).all()
    banner_dicts = [banner.to_dict() for banner in banners]  #字典生成式将所有的轮播图数据存放入字典中，以便返回给前端
    return restful.ok(data=banner_dicts)

#删除轮播图
@bp.post("/banner/delete")
@permission_required(Permission.BANNER)
def dalete_banner():
    banner_id = request.form.get("id") #因为这里只有一个数据，就不制作表单了
    if not banner_id:
        return restful.params_error(message="没有传入轮播图id")
    try:
        banner_modle = BannerModel.query.get(banner_id)
    except Exception as e:
        return restful.params_error(message="轮播图不存在")
    db.session.delete(banner_modle)
    db.session.commit()
    return restful.ok()

#编辑轮播图
@bp.post("/banner/edit")
@permission_required(Permission.BANNER)
def edit_banner():
    form =EditBannerForm(request.form)
    if form.validate():
        banner_id = form.id.data
        try:
            banner_model = BannerModel.query.get(banner_id)
        except Exception as e:
            return restful.params_error(message="轮播图不存在")
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data

        #获取新的数据以后，更新数据库中的数据
        banner_model.name = name
        banner_model.image_url = image_url
        banner_model.link_url = link_url
        banner_model.priority = priority
        db.session.commit()
        return restful.ok(data=banner_model.to_dict())
    else:
        message = form.messages[0]  # 每次只返回第一条错误信息
        return restful.params_error(message=message)

############轮播图管理页面##########################

################帖子管理页面###########################
#获取帖子列表(分页)
@bp.get("/post/list")
@permission_required(Permission.POST)
def post_list():
    page = request.args.get('page',default=1,type=int) #前端需要当前页码，要传过去
    start = (page - 1) * current_app.config['PER_PAGE_COUNT']
    end = start + current_app.config['PER_PAGE_COUNT']
    query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    total_count = query_obj.count() #获取帖子总数,EP组件需要传入这个参数
    posts = query_obj.slice(start,end) #分页切片，是个列表，需要转换为字典格式返回给前端
    post_list= [post.to_dict() for post in posts]
    return restful.ok(data={'total_count':total_count,"post_list":post_list,"page":page})

#删除帖子
@bp.post("/post/delete")
@permission_required(Permission.POST)
def dalete_post():
    post_id = request.form.get("id") #因为这里只有一个数据，就不制作表单了
    if not post_id:
        return restful.params_error(message="没有传入帖子id")
    try:
        post_modle = PostModel.query.get(post_id)
    except Exception as e:
        return restful.params_error(message="帖子不存在")
    db.session.delete(post_modle)
    db.session.commit()
    return restful.ok()
################帖子管理页面###########################


################评论管理页面###########################
#获取评论列表
@bp.get("/comment/list")
@permission_required(Permission.COMMENT)
def comment_list():
    comments=CommentModel.query.order_by(CommentModel.create_time.desc()).all()
    comment_dicts = [comment.to_dict() for comment in comments]
    return restful.ok(data=comment_dicts)

@bp.post("/comment/delete")
@permission_required(Permission.COMMENT)
def delete_comment():
    comment_id = request.form.get("id")
    if not comment_id:
        return restful.params_error(message="没有传入评论id")
    try:
        comment_modle = CommentModel.query.get(comment_id)
    except Exception as e:
        return restful.params_error(message="评论不存在")
    db.session.delete(comment_modle)
    db.session.commit()
    return restful.ok()
################评论管理页面###########################

################用户管理页面###########################
#获取用户列表
@bp.get("/user/list")
@permission_required(Permission.USER)
def user_list():
    users=UserModel.query.order_by(UserModel.join_time.desc()).all()
    user_dicts_list = [user.to_dict() for user in users]
    return restful.ok(data=user_dicts_list)

#用户激活
@bp.post("/user/active")
@permission_required(Permission.USER)
def user_active():
    #表单包含用户id何激活状态，这里简单表示
    is_active = request.form.get("is_active", type=int)
    user_id = request.form.get("id")
    user =UserModel.query.get(user_id) #这里出来的is_acitve是字符串类型'0'，因为里面有内容，回一直判断为true
    user.is_active = bool(is_active)
    db.session.commit()
    return restful.ok(data=user.to_dict())
################用户管理页面###########################



#################后台首页#############################
@bp.get("/board/post/count")
def board_post_count():
    #获取板块下的帖子数量
    board_post_count_list = db.session.query(BoardModel.name, func.count(BoardModel.name)).join(PostModel).group_by(BoardModel.name).all()
    #print(board_post_count_list)#query(BoardModel.name, func.count(BoardModel.name) query里面就是获取到的数据
    # 输出结果[('Django', 15), ('Flask', 13), ('Python', 31), ('前端', 22), ('爬虫', 18)]
    board_names=[]
    post_counts=[]
    for bc in board_post_count_list:
        board_names.append(bc[0]) #横坐标数据
        post_counts.append(bc[1]) #纵坐标数据
    return restful.ok(data={"board_names":board_names,"post_counts":post_counts})

@bp.get("/day7/post/count")
def day7_post_count():
    #获取日期，帖子数量
    #因为日期是以datetime形式存储，读取的时候需要借助日期格式化函数，才能进行分类或比较 参考文档https://blog.csdn.net/fuu123f/article/details/109359464
    #MySQL数据库用的是date_format函数

    now = datetime.now() #获取当前日期
    #获取的是7天前0点0分的日期，一定要把毫秒都减为0，不让当前时间之前的帖子就获取不到了
    seven_day_ago=now -timedelta(days=6,hours=now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    #查找近七天发的帖子数量
    day7_post_count_list=db.session.query(func.date_format(PostModel.create_time, "%Y-%m-%d"), func.count(PostModel.id)).group_by(func.date_format(
        PostModel.create_time, "%Y-%m-%d")).filter(PostModel.create_time>=seven_day_ago).all()#[('2024-07-26', 2)]
    day7_post_count_dict = dict(day7_post_count_list) #原来又列表又元组的，现在转换成字典，方便拿数据 {'2024-07-26': 2}
    #添加循环，让七天内就算没有发帖数也能补充正确的数据
    for x in range(7):
        date = seven_day_ago+timedelta(days=x)
        date_str = date.strftime("%Y-%m-%d")
        if date_str not in day7_post_count_dict:
            day7_post_count_dict[date_str]=0  #如果日期的键不在七日数据字典中，就说明那天没发帖，将那天发帖量定为0，并将该键值对存入字典中

    #给日期排序 小到大
    dates = sorted(list(day7_post_count_dict.keys())) #折线图横坐标
    counts = [] #折线图纵坐标
    for day in dates:
        counts.append(day7_post_count_dict[day])
    return restful.ok(data={"dates":dates,"counts":counts})
#################后台首页#############################



