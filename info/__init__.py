from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config import config_dict
from info.modules.home import home_blu


def create_app(config_type):  # 定义函数来封装应用的创建  工厂函数
    config_class = config_dict[config_type]
    app = Flask(__name__)
    # 根据配置类来加载应用配置
    app.config.from_object(config_class)
    # 创建mysql数据库连接对象
    db = SQLAlchemy(app)
    # 创建redis数据库连接对象
    sr = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    # 初始化session存储对象
    Session(app)
    # 初始化迁移器
    Migrate(app, db)

    # 注册蓝图
    app.register_blueprint(home_blu)

    return app
