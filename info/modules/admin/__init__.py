from flask import Blueprint, request, session, current_app, g, redirect

from info.models import User

admin_blu = Blueprint("admin", __name__, url_prefix="/admin")  # 创建蓝图对象


# 使用蓝图的请求钩子,对后台访问进行控制
@admin_blu.before_request
def check_superuser():
    # 判断是否是管理员登陆
    is_admin = session.get("is_admin")
    # 如果没有后台登陆,并且不是访问后台登陆页面,那么就返回到首页
    if not is_admin and not request.url.endswith("admin/login"):
        return redirect("/")


from .views import *
