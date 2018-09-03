from flask import g, redirect, render_template, request, jsonify, abort

from info.common import user_login_data
from info.modules.user import user_blu

# 显示个人中心
from info.utils.response_code import RET, error_map


@user_blu.route('/user_info')
@user_login_data
def user_info():
    # 判断用户是否登陆
    user = g.user

    if not user:
        return redirect('/')

    user = user.to_dict() if user else None

    # 如果已登陆
    return render_template("news/user.html", user=user)


# 显示基本信息
@user_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    # 判断用户是否登陆
    user = g.user
    if not user:
        return abort(404)

    # get请求
    if request.method == "GET":
        # 根据user显示用户的基本信息

        return render_template("news/user_base_info.html", user=user)

    # post请求
    # 获取参数
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    # 校验参数
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 修改模型数据
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
