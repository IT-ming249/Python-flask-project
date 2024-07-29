from exts import db
import shortuuid
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy_serializer import SerializerMixin #参考文档 https://www.zlkt.net/post/detail/61

class UserModel(db.Model, SerializerMixin): #序列货orm模型需要继承SerializerMixin
    #serialize_rules = ("-_password", ) # -_password表示序列化时排除 _password字段。 但这样会出现循环系列化问题
    serialize_only = ("id","email","username","avatar","signature","join_time","is_staff","is_active","role_id","role") #这是一种解决循环序列化的方法
    __tablename__= 'user' #表名
    id = db.Column(db.String(100),primary_key =True, default=shortuuid.uuid) #shortuuid.uuid生成短唯一标识符（UUID）
    email = db.Column(db.String(50),unique=True,nullable=False) #邮箱，唯一不重复
    username = db.Column(db.String(50),nullable=False)
    _password = db.Column(db.String(252),nullable = False) #存放加密后的密码
    #realname = db.Column(db.String(50))
    avatar = db.Column(db.String(50))#头像
    signature = db.Column(db.String(100))#签名S
    join_time = db.Column(db.DateTime, default=datetime.now()) #DateTime是SQLAlchemy中表示日期和时间的数据类型
    is_staff = db.Column(db.Boolean, default = False) #判断是否公司员工
    is_active = db.Column(db.Boolean, default = True)

    ##权限相关
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("RoleModel", backref="users")

    #*args表示所有未知参数, **kwargs表示所有带关键字的参数eg:'pasword=11,**kwargs是个字典' ,这两个组合就可以代表所有的参数
    def __init__(self, *args, **kwargs):
        if "password" in kwargs:
            self.password = kwargs.get('password') # 如果输入了密码，就把password键对应的值取出来
            kwargs.pop("password")                      #将password键从kwargs字典中删除，以防止将其传递给父类的构造函数。
        super(UserModel, self).__init__(*args,**kwargs) #按照父类创建一个实例化对象，只是password变成了加密后的

    @property
    def password(self):  # 访问 通过该属性访问的密码也是加密后的
        return self._password
        # @property装饰器用于将password方法转换为只读属性。这意味着在访问password属性时，实际上是调用了password方法，而不是直接访问属性
        # 使用后可以用 UserModel.password访问该方法，而不是UserModel.password()

    @password.setter
    def password(self, newpwd):  # 赋值 将self.password = kwargs.get('password')取出的值当作参数newpwd传入password方法中
        self._password = generate_password_hash(newpwd)  # 将newpwd加密后赋值给_password

    #密码验证方法
    def check_password(self,rawpwd): #检查密码，需要传入明文密码
        return check_password_hash(self.password,rawpwd)

    #权限判断方法
    def has_permission(self,permission):
        #当前用户拥有的权限与permission相与
        return (self.role.permissions & permission)==permission


class Permission(object): #python所有类都继承object这个基类
    # 255的二进制方式来表示 1111 1111 0b表示二进制   判断用户有哪个权限，就将用户的权限与ALL_PERMISSION相与
    ALL_PERMISSION = 0b11111111
    # 1. 访问者权限
    VISITOR = 0b00000001
    # 2. 管理帖子权限
    POST = 0b00000010
    # 3. 管理评论的权限
    COMMENT = 0b00000100
    # 4. 管理板块的权限
    BANNER = 0b00001000
    # 5. 管理前台用户的权限
    USER = 0b00010000
    # 6. 管理后台管理员的权限
    STAFF = 0b01000000

#权限管理模型
class RoleModel(db.Model, SerializerMixin):
    serialize_only = ("id", "name", "desc", "create_time")
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(200),nullable=True) #描述信息
    create_time = db.Column(db.DateTime,default=datetime.now)
    permissions = db.Column(db.Integer,default=Permission.VISITOR) #权限 权限可以不告诉前端




