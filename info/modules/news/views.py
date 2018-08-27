from flask import render_template, current_app, abort, g, jsonify, request

from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News
from info.modules.news import news_blu
from info.utils.response_code import RET, error_map


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

    user = g.user  # 取出user
    is_collected = False  # 没有收藏
    # 判断用户是否收藏
    if user:
        if news in user.collection_news:
            is_collected = True  # 已收藏

    user = user.to_dict() if user else None

    return render_template("news/detail.html", news=news.to_dict(), rank_list=rank_list, user=user,
                           is_collected=is_collected)


# 新闻收藏
@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 先判断用户是否登陆
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 将字符串转化为整型
    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 根据action执行不同的处理
    if action == "collect":  # 收藏
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:  # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
