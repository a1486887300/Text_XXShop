import logging
from django.http import HttpResponse
from django.shortcuts import render
import random
# Create your views here.
# GET /image_codes/(?P<image_code_id>[\w-]+)/
from rest_framework.response import Response
from rest_framework.views import APIView
from XXshop.libs.captcha.captcha import captcha
from XXshop.libs.yuntongxun.sms import CCP
# 不需要操作数据库  直接用APIView
from . import constants
from .serializers import CheckImageCodeSerializer
from django_redis import get_redis_connection

# 获取日志器
# logger=logging.getLog('django')
logger = logging.getLogger('django')


# 手机验证码
# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(APIView):
    """
    发送短信验证码:
    1.接收参数并进行参数校验(参数合法性教研,图片验证码对比)
    2.使用云通讯发送短息验证码
    3.返回应答发送成功
    """

    def get(self, request, mobile):
        # 1.接收参数并进行参数校验(参数合法性教研, 图片验证码对比)
        # serializer = CheckImageCodeSerializer(data=requset.query_parms)
        serializer = CheckImageCodeSerializer(data=request.query_params, context={'view': self})

        serializer.is_valid(raise_exception=True)

        # 2.使用云通讯发送短息验证码
        # 随机生成6位短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        logger.info('短信验证码为: %s' % sms_code)

        # 在redis 中保存短信验证码
        redis_con = get_redis_connection('verify_codes')

        redis_con.setex('img_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 使用云通讯发送短信验证码
        # try:
        #     expire = constants.SMS_CODE_REDIS_EXPIRES // 60
        #
        #     res = CCP().send_template_sms(mobile, [sms_code, expire], constants.SMS_CODE_TEMP_ID)
        #
        # except Exception as e:
        #     logger.error(e)
        #     return Response({'message': '发送短信异常'})
        #
        # else:
        #
        #     if res != 0:
        #         logger.error('发送短信失败')
        #         return Response({'message': '发送短信失败'})

        # 3.返回应答发送成功
        return Response({'message': '发送短信成功'})


# 图片验证码
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
        logger.info('图片验证码为: %s' % text)

        # 返回验证码图片
        return HttpResponse(image, content_type='image/jpg')
