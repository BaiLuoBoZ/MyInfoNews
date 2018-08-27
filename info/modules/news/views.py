from flask import render_template, current_app, abort, g

from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News
from info.modules.news import news_blu


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):  # 显示新闻详情
    # 根据news_id取出新闻详情
    news = None
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)

    if not news:
        return abort(404)

    # 点击量+1
    news.clicks += 1

    # 显示点击排行 取出点击量最高的前十条新闻,并且倒序排列
    rank_list = []
    try:
        rank_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    except BaseException as e:
        current_app.logger.error(e)

    rank_list = [news.to_basic_dict() for news in rank_list]

    user = g.user
    user = user.to_dict() if user else None

    return render_template("news/detail.html", news=news.to_dict(), rank_list=rank_list, user=user)
