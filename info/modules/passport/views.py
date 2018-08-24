from flask import request, abort, current_app, make_response, Response

from info import sr
from info.modules.passport import passport_blu
from info.utils.captcha.pic_captcha import captcha


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
