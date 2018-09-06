import time
from datetime import datetime, timedelta

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


# 退出登陆
@admin_blu.route('/logout')
def logout():
    session.pop("user_id", None)
    session.pop("is_admin", None)

    return redirect('/')


# 用户统计
@admin_blu.route('/user_count')
def user_count():
    # 用户总数
    user_count = 0
    try:
        user_count = User.query.filter(User.is_admin == False).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 用户月新增人数   当月1号到当前时间
    mon_user_count = 0
    # 获取本地日期
    t = time.localtime()
    # 先构建日期字符串
    date_mon_str = "%d-%02d-01" % (t.tm_year, t.tm_mon)
    # 日期字符串可以转换为日期对象
    date_mon = datetime.strptime(date_mon_str, "%Y-%m-%d")
    # 查询用户月新增人数
    try:
        mon_user_count = User.query.filter(User.is_admin == False, User.create_time >= date_mon).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 用户日新增人数
    day_user_count = 0
    # 先构建日期字符串
    date_day_str = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    # 将日期字符串转换为日期对象
    date_day = datetime.strptime(date_day_str, "%Y-%m-%d")
    # 查询用户日新增人数
    try:
        day_user_count = User.query.filter(User.is_admin == False, User.create_time >= date_day).count()
    except BaseException as e:
        current_app.logger.error(e)

    # 获取日活跃人数(每日的登陆人数)
    active_count = []
    active_time = []
    try:
        for i in range(30):
            begin_date = date_day - timedelta(days=i)
            end_date = date_day + timedelta(days=1 - i)
            one_day_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                              User.last_login < end_date).count()
            active_count.append(one_day_count)
            # 将日期对象转化为日期字符串
            one_day_str = begin_date.strftime("%Y-%m-%d")
            active_time.append(one_day_str)
    except BaseException as e:
        current_app.logger.error(e)

    active_time.reverse()
    active_count.reverse()

    data = {
        "user_count": user_count,
        "day_user_count": day_user_count,
        "mon_user_count": mon_user_count,
        "active_time":active_time,
        "active_count":active_count
    }

    return render_template("admin/user_count.html", data=data)


