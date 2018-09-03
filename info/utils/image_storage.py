import qiniu

# 需要填写你的 Access Key 和 Secret Key
access_key = 'kJ8wVO7lmFGsdvtI5M7eQDEJ1eT3Vrygb4SmR00E'
secret_key = 'rGwHyAvnlLK7rU4htRpNYzpuz0OHJKzX2O1LWTNl'
# 要上传的空间
bucket_name = 'infonews'


def upload_img(data):
    """
    上传文件
    :param data: 上传的文件 bytes
    :return: 上传后的文件名
    """
    q = qiniu.Auth(access_key, secret_key)
    key = None  # 上传的文件名  如果设置为None, 会生成随机名称
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, key, data)
    if ret is not None:
        return ret.get("key")
    else:
        raise BaseException(info)


if __name__ == '__main__':
    with open("/Users/zhangzz/Desktop/123.jpg", "rb") as f:
        img_bytes = f.read()
        try:
            file_name = upload_img(img_bytes)
            print(file_name)
        except BaseException as e:
            print(e)