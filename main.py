from datetime import timedelta

from flask import Flask, session
from flask_session import Session
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
    # 指定session存储的数据库类型
    SESSION_TYPE = "redis"
    # 设置session存储使用的redis对象
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 对cookie中保存的sessionid进行加密
    SESSION_USE_SIGNER = True
    # 应用秘钥
    SECRET_KEY = "j7u1TSTgxEXcjJIqrauuHirMfLZnbGAbHRVopZftM5/w0PLGduhUcVHY95dIg8So9Mip+hnl39W1N1jPgimxXA=="
    # 设置session存储时间
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


app = Flask(__name__)
# 根据配置类来加载应用配置
app.config.from_object(Config)
# 创建mysql数据库连接对象
db = SQLAlchemy(app)
# 创建redis数据库连接对象
sr = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 初始化session存储对象
Session(app)


@app.route('/')
def index():
    session["name"] = "lisi"
    return "index"


if __name__ == '__main__':
    app.run()
