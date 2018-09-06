import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, redirect, url_for, session, abort, jsonify

from info.constants import USER_COLLECTION_MAX_NEWS
from info.models import User, News
from info.modules.admin import admin_blu

# 显示后台管理
from info.utils.response_code import RET, error_map


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
        "active_time": active_time,
        "active_count": active_count
    }

    return render_template("admin/user_count.html", data=data)


# 显示用户列表
@admin_blu.route('/user_list')
def user_list():
    # 获取参数
    page = request.args.get("p", 1)  # 获取当前页码

    # 检验参数
    if not page:
        return abort(404)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 查询当前页的用户信息
    user_list = []
    try:
        pn = User.query.filter(User.is_admin == False).paginate(page, USER_COLLECTION_MAX_NEWS)

        user_list = pn.items
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        total_page = 1

    data = {
        "user_list": [user.to_admin_dict() for user in user_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("admin/user_list.html", data=data)


# 显示新闻审核列表
@admin_blu.route('/news_review')
def news_review():
    # 获取参数
    page = request.args.get("p", 1)  # 获取当前页码

    # 检验参数
    if not page:
        return abort(404)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 查询当前页的新闻审核列表
    news_list = []
    try:
        pn = News.query.filter(News.user_id != 0).paginate(page, USER_COLLECTION_MAX_NEWS)

        news_list = pn.items
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        total_page = 1

    data = {
        "news_list": [news.to_review_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("admin/news_review.html", data=data)


# 显示审核新闻
@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    # 根据新闻id取出新闻模型
    news = None
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)

    news = news.to_dict() if news else None

    return render_template("admin/news_review_detail.html", news=news)


# 提交新闻审核详情
@admin_blu.route('/news_review_action', methods=['GET', 'POST'])
def news_review_action():
    # 获取参数
    action = request.json.get("action")
    news_id = request.json.get("news_id")
    reason = request.json.get("reason")

    # 校验参数
    if not all([action, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if not action in ["accept", "reject"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    if action == "accept":  # 审核通过
        news.status = 0

    else:  # 审核未通过
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
        # 修改审核状态,并保存审核未通过原因
        news.status = -1
        news.reason = reason

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 新闻版式编辑列表显示
@admin_blu.route('/news_edit')
def news_edit():
    # 获取参数
    page = request.args.get("p", 1)  # 获取当前页码

    # 检验参数
    if not page:
        return abort(404)

    try:
        page = int(page)
    except BaseException as e:
        current_app.logger.error(e)
        page = 1

    # 查询当前页的新闻审核编辑列表
    news_list = []
    try:
        pn = News.query.order_by(News.create_time.desc()).paginate(page, USER_COLLECTION_MAX_NEWS)

        news_list = pn.items
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        total_page = 1

    data = {
        "news_list": [news.to_review_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("admin/news_edit.html", data=data)
