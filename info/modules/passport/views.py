import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, Response, jsonify, session

from info import sr, db
from info.lib.yuntongxun.sms import CCP
from info.models import User
from info.modules.passport import passport_blu
from info.utils.captcha.pic_captcha import captcha
from info.utils.response_code import RET, error_map


@passport_blu.route('/get_img_code')  # 获取图片验证码
def get_img_code():
    # 获取参数
    img_code_id = request.args.get("img_code_id")  # 拿到图片的key
    # 校验参数
    if not img_code_id:
        return abort(403)  # 如果参数错误，那么直接返回403

    # 生成图片验证码
    img_name, img_code_text, img_code_bytes = captcha.generate_captcha()

    # 将图片key和验证码文字保存到数据库中
    try:
        sr.set("img_code_id" + img_code_id, img_code_text, ex=180)
    except BaseException as e:
        # 将错误信息保存到日志中
        current_app.logger.error(e)
        return abort(500)

    # 返回验证码图片
    response = make_response(img_code_bytes)  # type:Response
    response.content_type = "image/jpeg"

    return response


# 获取短信验证码
@passport_blu.route('/get_sms_code', methods=["POST"])
def get_sms_code():
    # 获取参数  手机号码 用户输入的验证码 图片key
    mobile = request.json.get("mobile")
    img_code = request.json.get("img_code")
    img_code_id = request.json.get("img_code_id")
    # 校验参数
    if not all([mobile, img_code_id, img_code]):
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 校验手机号码的格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg=error_map[RET.DATAERR])

    # 校验图片验证码是否过期
    try:
        real_img_code = sr.get("img_code_id" + img_code_id)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not real_img_code:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码已过期！")

    # 判断用户输入的验证码是否正确
    if real_img_code != img_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码输入错误！")

    # 判断用户输入的手机号码是否注册过
    user = User.query.filter_by(mobile=mobile).first()
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg=error_map[RET.DATAEXIST])

    # 获取4位随机数字
    sms_code = "%04d" % random.randint(0, 9999)
    current_app.logger.error("短信验证码为：%s" % sms_code)
    # 发送短信
    res_code = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # 判断短信是否发送成功
    if res_code == -1:
        return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # 将短信验证码保存到redis,并设置有效期为一分钟
    try:
        sr.set("sms_code_id" + mobile, sms_code, ex=60)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户注册
@passport_blu.route('/register', methods=["POST"])
def register():
    # 获取参数 手机号 密码 短信验证码
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    sms_code = request.json.get("sms_code")
    # 参数校验
    if not all([mobile, password, sms_code]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 校验手机号码的格式是否正确
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg=error_map[RET.DATAERR])

    # 判断短信验证码是否过期
    try:
        real_sms_code = sr.get("sms_code_id" + mobile)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码已过期！")

    # 判断用户输入的验证码是否正确
    if real_sms_code != sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码输入错误！")

    # 将手机号、密码保存到mysql数据库
    user = User()
    user.mobile = mobile
    user.password = password
    user.nick_name = mobile
    user.last_login = datetime.now()

    try:
        db.session.add(user)
        db.session.commit()
    except BaseException as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 状态保持,免密码登陆
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 用户登陆
@passport_blu.route('/login', methods=['POST'])
def login():
    # 获取参数  手机号 密码
    mobile = request.json.get("mobile")
    password = request.json.get("password")

    # 校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 校验手机号码的格式是否正确
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg=error_map[RET.DATAERR])

    # 判断用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not user:
        return jsonify(errno=RET.USERERR, errmsg=error_map[RET.USERERR])

    # 用户存在,判断密码是否正确
    if not user.check_password(password):  # 密码错误
        return jsonify(errno=RET.PWDERR, errmsg=error_map[RET.PWDERR])

    # 记录用户的最后登陆时间
    user.last_login = datetime.now()

    # 状态保持
    session["user_id"] = user.id

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
