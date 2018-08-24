from flask import render_template, current_app

from info.modules.home import home_blu


@home_blu.route('/')  # 使用蓝图来装饰路由
def index():
    print(current_app.url_map)
    return render_template("index.html")


@home_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
