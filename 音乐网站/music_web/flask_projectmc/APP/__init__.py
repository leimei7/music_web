#初始化
#创建flask应用
from flask import Flask
from .views import blue
from .exts import init_exts

def create_app():
    app=Flask(__name__)

    app.register_blueprint(blueprint=blue)#注册蓝图，链接蓝图与app

    # 配置数据库
    #db_uri = 'sqlite:///sqlite3.db' #sqllite

    db_uri = 'mysql+pymysql://leimei7:*****@localhost:3306/musicdb' #mysql

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    # 链接路径

    # 初始化插件
    init_exts(app=app)

    return app