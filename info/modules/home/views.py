from flask import render_template, current_app, session

from info.models import User
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

    return render_template("index.html", user=user) # 将用户信息传到模板中


@home_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
