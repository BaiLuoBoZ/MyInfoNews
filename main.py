from flask import Flask, session
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config import Config

app = Flask(__name__)
# 根据配置类来加载应用配置
app.config.from_object(Config)
# 创建mysql数据库连接对象
db = SQLAlchemy(app)
# 创建redis数据库连接对象
sr = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 初始化session存储对象
Session(app)
# 创建管理器
mgr = Manager(app)
# 初始化迁移器
Migrate(app, db)
# 添加迁移命令
mgr.add_command("mc", MigrateCommand)


@app.route('/')
def index():
    session["name"] = "lisi"
    return "index"


if __name__ == '__main__':
    mgr.run()
