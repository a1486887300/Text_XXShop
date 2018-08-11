from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
# GET /image_codes/(?P<image_code_id>[\w-]+)/
from rest_framework.views import APIView
from XXshop.libs.captcha.captcha import captcha

# 不需要操作数据库  直接用APIView
from . import constants

from django_redis import get_redis_connection


class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        """
        获取图片验证码
        """
        # 接受参数并进行数据校验 (APIView)

        # 产生验证图片验证码
        text, image = captcha.generate_captcha()

        # 在redis的verify_codes(根据设置文件配置)数据库中保存图片验证码文本内容
        redis_con = get_redis_connection('verify_codes')

        # setex(验证码图片名,有效时间,验证码文本)
        redis_con.setex('img_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 返回验证码图片
        return HttpResponse(image, content_type='image/jpg')
