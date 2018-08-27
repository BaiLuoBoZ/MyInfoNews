from flask import render_template, current_app, session

from info.constants import CLICK_RANK_MAX_NEWS
from info.models import User, News
from info.modules.home import home_blu


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

    return render_template("index.html", user=user, rank_list=rank_list)  # 将用户信息传到模板中


@home_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
