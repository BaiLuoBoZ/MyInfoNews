from flask import g, redirect, render_template, request, jsonify, abort, current_app

from info import db
from info.common import user_login_data
from info.constants import USER_COLLECTION_MAX_NEWS, QINIU_DOMIN_PREFIX
from info.models import tb_user_collection, Category, News
from info.modules.user import user_blu

from info.utils.image_storage import upload_img
from info.utils.response_code import RET, error_map


# 显示个人中心
@user_blu.route('/user_info')
@user_login_data
def user_info():
    # 判断用户是否登陆
    user = g.user

    if not user:
        return redirect('/')

    user = user.to_dict()

    # 如果已登陆
    return render_template("news/user.html", user=user)


# 显示基本信息
@user_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    # 判断用户是否登陆
    user = g.user
    if not user:
        return abort(404)

    # get请求
    if request.method == "GET":
        # 根据user显示用户的基本信息

        return render_template("news/user_base_info.html", user=user)

    # post请求
    # 获取参数
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    # 校验参数
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 修改模型数据
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 显示/修改头像
@user_blu.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    user = g.user
    # 判断是否登陆
    if not user:
        return abort(404)

    # get 请求
    if request.method == "GET":
        return render_template("news/user_pic_info.html", user=user.to_dict())

    # post 请求
    # 获取参数
    avatar = request.files.get("avatar")

    # 校验参数
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 上传文件
    try:
        img_bytes = avatar.read()
        file_name = upload_img(img_bytes)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # 保存到数据库
    user.avatar_url = file_name

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_dict())


# 密码修改
@user_blu.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    # 判断用户是否登陆
    user = g.user
    if not user:
        return abort(404)

    # get 请求
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    # POST 请求
    # 获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    # 校验参数
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 判断旧密码是否正确
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR, errmsg=error_map[RET.PWDERR])

    # 保存新的密码
    user.password = new_password

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 显示我的收藏列表
@user_blu.route('/collection')
@user_login_data
def collection():
    # 判断用户是否登陆
    user = g.user
    if not user:
        return abort(404)

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

    # 查询当前用户收藏的新闻
    news_list = []
    try:
        pn = user.collection_news.order_by(tb_user_collection.c.create_time.desc()).paginate(page,
                                                                                             USER_COLLECTION_MAX_NEWS)
        news_list = pn.items
        total_page = pn.pages
    except BaseException as e:
        current_app.logger.error(e)
        total_page = 1

    data = {
        "news_list": [news.to_dict() for news in news_list],
        "cur_page": page,
        "total_page": total_page
    }

    return render_template("news/user_collection.html", data=data)


# 新闻发布
@user_blu.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    # 判断用户是否登陆
    user = g.user
    if not user:
        return abort(404)

    # get请求
    if request.method == "GET":
        # 查询所有的新闻分类
        categories = []
        try:
            categories = Category.query.all()
        except BaseException as e:
            current_app.logger.error(e)
            return abort(404)

        if not categories:
            return abort(404)

        category_list = [category.to_dict() for category in categories]

        if category_list:
            category_list.pop(0)

        # 渲染页面
        return render_template("news/user_news_release.html", category_list=category_list)

    # post 请求
    # 获取参数
    title = request.form.get("title")  # 标题
    category_id = request.form.get("category_id")  # 新闻分类
    digest = request.form.get("digest")  # 新闻摘要
    index_image = request.files.get("index_image")  # 图片
    content = request.form.get("content")  # 新闻内容

    # 校验参数
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        category_id = int(category_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 创建新的新闻模型
    news = News()
    # 保存数据
    news.title = title
    news.category_id = category_id
    news.digest = digest
    news.content = content
    # 新闻来源
    news.source = "朱哥出品,必属精品!"
    # 当前新闻作者
    news.user_id = user.id
    # 当前新闻审核状态  1 表示审核中
    news.status = 1
    # 保存新闻列表图片路径
    try:
        file_name = upload_img(index_image.read())
        news.index_image_url = QINIU_DOMIN_PREFIX + file_name
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # 提交
    try:
        db.session.add(news)
        db.session.commit()
    except BaseException as e:
        db.session.rollback()  # 回滚
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 返回json状态
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
