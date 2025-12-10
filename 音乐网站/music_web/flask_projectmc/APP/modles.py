#模型，与数据库相关
from .exts import db

#模型，类
#基础与db
class MSelect(db.Model):
    __tablename__='select'
    mid=db.Column(db.String(16),primary_key=True,unique=True)
    name=db.Column(db.String(60),index=True)
    singer=db.Column(db.String(60),index=True)
    id=db.Column(db.Integer,autoincrement=True)

class MDownload(db.Model):
    __tablename__='download'
    mid=db.Column(db.String(16),primary_key=True,unique=True)
    name=db.Column(db.String(60),index=True)
    singer=db.Column(db.String(60),index=True)
    music_src=db.Column(db.Text,default='C:/QMusic/')

class SetData(db.Model):
    __tablename__='setdata'
    id=db.Column(db.Integer,primary_key=True)
    U_key=db.Column(db.Text)
    sit=db.Column(db.Text,default='C:/QMusic/')
    flag=db.Column(db.Integer,default=6)
    passwd=db.Column(db.String(32),default='<PASSWORD>')
    name=db.Column(db.String(30),index=True)
    theme=db.Column(db.Integer,default=0)
    login_ok=db.Column(db.Boolean,default=False)
