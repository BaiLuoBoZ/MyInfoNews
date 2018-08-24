from flask import current_app

from info.modules.home import home_blu


@home_blu.route('/')  # 使用蓝图来装饰路由
def index():
    try:
        1 / 0
    except BaseException as e:
        current_app.logger.error("发现了一个错误 %s" % e)

    return "index"
