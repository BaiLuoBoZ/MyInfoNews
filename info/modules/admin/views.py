from flask import render_template, request, current_app, redirect, url_for, session, abort

from info.models import User
from info.modules.admin import admin_blu


# 显示后台管理
@admin_blu.route('/index')
def index():
    # 取出user_id
    user_id = session.get("user_id", None)
    if not user_id:
        return redirect(url_for("admin.login"))

    # 通过user_id 取出用户信息
    try:
        user = User.query.get(user_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(404)
    user = user.to_dict() if user else None

    return render_template("admin/index.html", user=user)


# 登陆后台
@admin_blu.route('/login', methods=['GET', 'POST'])
def login():
    # get 请求
    if request.method == "GET":
        # 判断用户是否登陆
        user_id = session.get("user_id")
        is_admin = session.get("is_admin")

        if not all([user_id, is_admin]):
            return render_template("admin/login.html")

        return redirect(url_for("admin.index"))

    # post 请求
    # 获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 校验参数
    if not all([username, password]):
        return render_template("admin/login.html", errmsg="用户名/密码不能为空!")

    # 查询数据库中是否有该用户
    try:
        user = User.query.filter(User.mobile == username).first()
    except BaseException as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="数据库错误!")

    if not user:
        return render_template("admin/login.html", errmsg="用户不存在!")

    # 判断是否是管理员账号
    if user.is_admin != True:
        return render_template("admin/login.html", errmsg="用户不存在!")

    # 判断密码是否正确
    if not user.check_password(password):
        return render_template("admin/login.html", errmsg="账户/密码错误!")

    # 状态保持
    session["user_id"] = user.id
    session["is_admin"] = user.is_admin

    # 密码正确,重定向到后台管理页面
    return redirect(url_for("admin.index"))
