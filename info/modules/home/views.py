from info.modules.home import home_blu


@home_blu.route('/')  # 使用蓝图来装饰路由
def index():
    return "index"