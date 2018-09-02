from flask import render_template, current_app, abort, g, jsonify, request

from info import db
from info.common import user_login_data
from info.constants import CLICK_RANK_MAX_NEWS
from info.models import News, Comment
from info.modules.news import news_blu
from info.utils.response_code import RET, error_map


# 显示新闻详情
@news_blu.route('/<int:news_id>')
@user_login_data
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

    # 显示该新闻所有评论信息
    comments = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()

    # 判断用户是否对某条评论点过赞
    comments_list = []
    for comment in comments:
        comments_dict = comment.to_dict()
        is_like = False
        if user:
            if comment in user.like_comments:
                is_like = True  # 已点赞
            comments_dict["is_like"] = is_like
        # 将评论字典加入到列表中
        comments_list.append(comments_dict)

    user = user.to_dict() if user else None

    return render_template("news/detail.html", news=news.to_dict(), rank_list=rank_list, user=user,
                           is_collected=is_collected, comments=comments_list)


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


# 新闻评论
@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_content = request.json.get("comment")
    news_id = request.json.get("news_id")
    parent_id = request.json.get("parent_id", 0)

    # 校验参数
    if not all([comment_content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        news_id = int(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据news_id查询新闻模型
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not news:
        # 该新闻不存在
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 建立评论模型
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:  # 判断parent_id是否为零
        try:
            parent_id = int(parent_id)
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
        # 存在父评论id,保存到数据库
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except BaseException as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=comment.to_dict())


# 评论点赞
@news_blu.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    # 判断用户是否登陆
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])

    # 获取参数
    comment_id = request.json.get("comment_id")  # 评论id
    action = request.json.get("action")

    # 校验参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        comment_id = int(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 根据comment_id取出评论模型
    try:
        comment = Comment.query.get(comment_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    # 根据action来执行相关操作
    if action == "add":  # 点赞
        if comment not in user.like_comments:
            user.like_comments.append(comment)
            comment.like_count += 1

    else:  # 取消点赞
        if comment in user.like_comments:
            user.like_comments.remove(comment)
            comment.like_count -= 1

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
