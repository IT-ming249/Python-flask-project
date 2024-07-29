from flask_mail import Message
from exts import mail
from celery import Celery


#定义任务函数
def send_mail(recipient,subject,body):
    message = Message(subject=subject,recipients=[recipient],body=body)
    try:
        mail.send(message)
        return {"status":"SUCCESS"}
    except Exception as e:
        return {"status": "FAILURE"}

#创建celery对象的工厂函数
def make_celery(app):
    celery  =Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL']) #创建一个celery对象
    TaskBase = celery.Task

    class ContextTask(TaskBase): #Celery中所有任务的父类
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self,*args,**kwargs)
    celery.Task = ContextTask
    app.celery = celery #讲celery绑定到app上，方便视图函数调用

    #添加任务
    celery.task(name="send_mail")(send_mail) #任务名称，以及任务函数 还有别的任务的话就定义新的任务函数，然后在这后面添加
    return celery