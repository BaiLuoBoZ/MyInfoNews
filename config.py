import logging
from datetime import timedelta

from redis import StrictRedis


class Config:  # 自定义配置类
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
    # 设置session存储时间(session会默认进行持久化)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopConfig(Config):  # 定义开发环境的配置
    DEBUG = True
    LOGLEVEL = logging.DEBUG


class ProductConfig(Config):  # 定义生产环境的配置
    DEBUG = False
    LOGLEVEL = logging.ERROR


config_dict = {
    "dev": DevelopConfig,
    "pro": ProductConfig
}
