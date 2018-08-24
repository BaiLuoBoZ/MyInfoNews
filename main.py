from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis


# 自定义配置类
class Config:
    DEBUG = True
    # 数据库的连接地址
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/myinfo16"
    # 是否跟踪数据库变化
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置redis的ip和端口号
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


app = Flask(__name__)
# 根据配置类来加载应用配置
app.config.from_object(Config)
# 创建mysql数据库连接对象
db = SQLAlchemy(app)
# 创建redis数据库连接对象
sr = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)


@app.route('/')
def index():
    sr.set("name", "zhangsan")
    print(sr.get("name"))
    return "index"


if __name__ == '__main__':
    app.run()
