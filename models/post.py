from exts import db
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
#板块模型
class BoardModel(db.Model,SerializerMixin):
    serialize_only = ("id","name","priority","create_time") #解决序列化postmodel时的死递归问题
    __tablename__= 'board'
    id = db.Column(db.Integer, primary_key=True, autoincrement =True) #id为自动增长的整数
    name = db.Column(db.String(20), unique =True)
    priority = db.Column(db.Integer, default =1) #优先级,数字越大，优先级越高
    create_time = db.Column(db.DateTime, default=datetime.now())

#帖子模型
class PostModel(db.Model,SerializerMixin):
    serialize_only = ("id","tittle","content","create_time","board","author")
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True, autoincrement =True)
    tittle = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False) #帖子内容的数据类型是Text
    create_time = db.Column(db.DateTime, default=datetime.now())
    board_id = db.Column(db.Integer, db.ForeignKey("board.id"))  #外键的数据类型要与原来的一致 表名.数据
    author_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    #引用
    board = db.relationship("BoardModel", backref=db.backref("posts")) #这样可通过 board.posts获取该板块下所有帖子, 序列化该模型时需要将BoardModel也序列化
    author = db.relationship("UserModel", backref=db.backref("posts")) #这样可通过 author.posts获取该用户的所有帖子

#轮播图模型
class BannerModel(db.Model,SerializerMixin):
    __tablename__ = 'banner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=False) #图片链接
    link_url = db.Column(db.String(255), nullable=False)  #跳转链接
    priority = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.now())

#评论模型
class CommentModel(db.Model,SerializerMixin):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text,nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    author_id = db.Column(db.String(100), db.ForeignKey("user.id"), nullable=False)
    #引用
    # 可通过 post.comments获取该帖子下所有评论，并规定了评论显示的顺序 cascade表示级联删除：帖子被删评论也跟着被删
    post = db.relationship("PostModel", backref=db.backref('comments',order_by="CommentModel.create_time.desc()",
                                                           cascade="delete, delete-orphan"))
    author = db.relationship("UserModel", backref=db.backref("comments"))