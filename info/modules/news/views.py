from flask import render_template, current_app, abort

from info.models import News
from info.modules.news import news_blu


@news_blu.route('/<int:news_id>')
def news_detail(news_id):
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

    return render_template("detail.html", news=news.to_dict())
