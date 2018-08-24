from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# 自定义配置类
class Config:
    DEBUG = True
    # 数据库的连接地址
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/myinfo16"
    # 是否跟踪数据库变化
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
# 根据配置类来加载应用配置
app.config.from_object(Config)
# 创建数据库连接对象
db = SQLAlchemy(app)


@app.route('/')
def index():
    return "index"


if __name__ == '__main__':
    app.run()
