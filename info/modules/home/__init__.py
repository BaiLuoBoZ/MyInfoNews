from flask import Blueprint

home_blu = Blueprint("home", __name__)  # 创建蓝图对象

from .views import *
