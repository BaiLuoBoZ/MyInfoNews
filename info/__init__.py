import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config import config_dict

# 将数据库操作对象全局化，方便其他文件操作数据库


db = None  # type:SQLAlchemy
sr = None  # type:StrictRedis


# 配置日志文件（将日志信息写入到文件中）
def setup_log(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_type):  # 定义函数来封装应用的创建  工厂函数
    config_class = config_dict[config_type]
    app = Flask(__name__)
    # 根据配置类来加载应用配置
    app.config.from_object(config_class)
    global db, sr
    # 创建mysql数据库连接对象
    db = SQLAlchemy(app)
    # 创建redis数据库连接对象
    sr = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, decode_responses=True)
    # 初始化session存储对象
    Session(app)
    # 初始化迁移器
    Migrate(app, db)

    # 注册蓝图
    from info.modules.home import home_blu
    app.register_blueprint(home_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    from info.modules.user import user_blu
    app.register_blueprint(user_blu)

    from info.modules.admin import admin_blu
    app.register_blueprint(admin_blu)

    # 配置日志信息
    setup_log(config_class.LOGLEVEL)

    # 让模型文件和主程序建立关联
    from info import models

    # 添加自定义过滤器
    from info.common import index_convert
    app.add_template_filter(index_convert, "index_convert")

    # 捕获404异常
    @app.errorhandler(404)
    def err_handler(e):
        return render_template("news/404.html")

    return app
