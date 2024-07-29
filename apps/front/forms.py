#编写注册页用户输入信息规范(注册表单)
from wtforms import Form, ValidationError
from wtforms.fields import StringField,IntegerField,FileField #文本字段类，用于处理字符串类型的输入
from wtforms.validators import Email, Length, EqualTo, InputRequired  #验证器
from flask_wtf.file import FileAllowed, FileSize
from models.auth import UserModel
from exts import cache
from flask import request


class BaseForm(Form):
    @property
    def messages(self):
        message_list=[]
        if self.errors:
            for errors in self.errors.values():
                message_list.extend(errors) #extend将errors列表中的元素全部添加到message_list列表中
        return message_list

class RegisterForm(BaseForm):
    #如果使用了Email这个validator,就必须要安装 pip install email_validator
    email = StringField(validators=[Email(message='请输入正确格式的邮箱！')])
    email_captcha = StringField(validators=[Length(6,6,message='请输入正确长度的验证码')]) #最短6位最长6位表示只能输入4位
    username = StringField(validators=[Length(3,20,message='请输入正确长度的用户名')])
    password = StringField(validators=[Length(6,20,message='请输入正确长度的密码')])
    repeat_password = StringField(validators=[EqualTo('password',message='两次输入的密码不一致')])
    graph_captcha = StringField(validators=[Length(4,4,message='请输入正确长度的图形验证码')])

    def validate_email(self,field): #在数据库中检查邮箱是否存在
        #这里函数名必须设置为validate_email，才能通过field.data获取邮箱数据 (validate_对象)
        email = field.data #获取邮箱
        user = UserModel.query.filter_by(email=email).first() #查找数据库中有无该邮箱
        if user:
            raise ValidationError(message='该用户已存在')
    def validate_email_captcha(self,field):
        email_captcha = field.data #获取用户提交的邮箱验证码
        email = self.email.data #获取邮箱
        cache_captcha = cache.get(email) #从缓存里获取发送的验证码
        if not cache_captcha or email_captcha != cache_captcha:
            raise ValidationError(message="邮箱验证码错误")

    def validate_graph_captcha(self,field):
        key = request.cookies.get("_graph_captcha_key") #从cookies中获取图行验证码的键
        cache_captcha = cache.get(key)  #从缓存中取出生成的验证码
        graph_captcha = field.data #获取用户提交的的验证码
        if not cache_captcha or graph_captcha.lower() != cache_captcha.lower():#验证码中有大写有小写，统一全部转成小写以后进行对比
            raise ValidationError(message="图形验证码有误")


class LoginForm(BaseForm):
    email = StringField(validators=[Email(message='请输入正确格式的邮箱！')])
    password = StringField(validators=[Length(6, 20, message='请输入正确长度的密码')])
    remember = IntegerField() #整型，1代表记住，0代表不记住，这个参数可以不传所以不用验证器

class UploadImageForm(BaseForm):
    image = FileField(validators=[FileAllowed(['jpg','jpeg','png'],message="图片格式不符合要求"),
                                  FileSize(max_size=1024*1024*5, message='图片最大不超过5M')])

class EditProfileForm(BaseForm):
    signature = StringField(validators=[Length(1,50,message='个性签名在1到50字之间')])

class PublicPostForm(BaseForm):
    tittle = StringField(validators=[Length(1, 200, message='标题在1到200字之内')])
    board_id = IntegerField(validators=[InputRequired(message="请传入板块id")])
    content = StringField(validators=[InputRequired(message='请输入内容')])

class PublicCommentForm(BaseForm):
    content = StringField(validators=[InputRequired(message='请输入内容')])
    post_id = IntegerField(validators=[InputRequired(message="请传入帖子id")])








