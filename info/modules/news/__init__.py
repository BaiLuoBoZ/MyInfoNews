from flask import Blueprint

news_blu = Blueprint("news", __name__,url_prefix="/news")  # 创建蓝图对象

from .views import *
