from models.post import BoardModel,PostModel
from models.auth import UserModel,RoleModel,Permission
from exts import db
import random


#flask可以自定义命令
#创建板块
def init_boards():
    borad_names = ['Python','Flask','Django','爬虫','前端']
    for index,bn in enumerate(borad_names): #index为索引
        board = BoardModel(name=bn, priority=len(borad_names)-index)
        db.session.add(board)
    db.session.commit()
    print('板块初始化成功')

#创建测试帖子
def create_test_posts():
    boards = list(BoardModel.query.all())
    board_count= len(boards)
    for x in range(99):
        tittle = "测试标题%d"%x
        content = "测试内容%d"%x
        author = UserModel.query.first()
        index = random.randint(0,board_count-1) #帖子随机分配到各个板块
        board = boards[index]
        post_model = PostModel(tittle=tittle,content=content,author=author,board=board)
        db.session.add(post_model)
    db.session.commit()
    print('测试帖子添加成功')

#初始化各种角色
def init_roles():
    # 运营
    operator_role = RoleModel(name="运营", desc="负责管理帖子和评论",
                         permissions=Permission.POST | Permission.COMMENT | Permission.USER) #|表示或操作
    # 管理员
    admin_role = RoleModel(name="管理员", desc="负责整个网站的管理",
                      permissions=Permission.POST | Permission.COMMENT | Permission.USER | Permission.STAFF)
    # 开发者（权限是最大的）
    developer_role = RoleModel(name="开发者", desc="负责网站的开发", permissions=Permission.ALL_PERMISSION)

    db.session.add_all([operator_role, admin_role, developer_role])
    db.session.commit()
    print("角色添加成功！")

#绑定角色命令
def bind_roles():
    user1 = UserModel.query.filter_by(email="1045109874@qq.com").first()
    user2 = UserModel.query.filter_by(email="1045109875@qq.com").first()
    user3 = UserModel.query.filter_by(email="1045109876@qq.com").first()

    role1= RoleModel.query.filter_by(name="开发者").first()
    role2= RoleModel.query.filter_by(name="运营").first()
    role3= RoleModel.query.filter_by(name="管理员").first()

    user1.role =role1
    user2.role =role2
    user3.role =role3

    db.session.commit()
    print("用户和角色绑定成功")



