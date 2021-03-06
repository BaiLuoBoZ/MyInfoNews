import functools

from flask import session, current_app, g

from info.models import User


def index_convert(index):
    index_dict = {1: "first", 2: "second", 3: "third"}
    return index_dict.get(index, "")


def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 根据session判断用户是否登陆
        user_id = session.get("user_id")
        user = None
        if user_id:
            # 根据user_id查询用户
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)

        g.user = user

        return f(*args, **kwargs)

    return wrapper
