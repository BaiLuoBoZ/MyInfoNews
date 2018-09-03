from flask import render_template, current_app, session, request, jsonify

from info.constants import CLICK_RANK_MAX_NEWS, HOME_PAGE_MAX_NEWS
from info.models import User, News, Category
from info.modules.home import home_blu
from info.utils.response_code import RET, error_map


@home_blu.route('/')  # 使用蓝图来装饰路由
def index():
    # 根据session判断用户是否登陆
    user_id = session.get("user_id")
    user = None
    if user_id:
        # 根据user_id查询用户
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)

    user = user.to_dict() if user else None

    # 显示点击排行 取出点击量最高的前十条新闻,并且倒序排列
    rank_list = []
    try:
        rank_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)

    rank_list = [news.to_basic_dict() for news in rank_list]

    # 获取分类列表
    categories = []
    try:
        categories = Category.query.all()
    except BaseException as e:
        current_app.logger.error(e)

    return render_template("news/index.html", user=user, rank_list=rank_list, categories=categories)  # 将用户信息传到模板中


# 显示新闻列表
@home_blu.route('/get_news_list')
def get_news_list():
    # 获取参数
    cid = request.args.get("cid")  # 分类id
    cur_page = request.args.get("cur_page")  # 当前页码
    per_count = request.args.get("per_count", HOME_PAGE_MAX_NEWS)  # 每页的个数
    # 校验参数
    if not all([cid, cur_page]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 将参数转换成整型
    try:
        cid = int(cid)
        cur_page = int(cur_page)
        per_count = int(per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据不同的cid显示不同的新闻
    filter_list = [News.status == 0]
    if cid != 1:
        filter_list.append(News.category_id == cid)

    # 根据参数查询新闻数据
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page, per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    data = {
        "total_page": pn.pages,
        "news_list": [news.to_dict() for news in pn.items]
    }

    # 将数据以json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=data)


@home_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
