from django_redis import get_redis_connection
from rest_framework import serializers

"""图片验证码序列化器类"""


class CheckImageCodeSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField(label='图片验证码uuid')
    text = serializers.CharField(label='图片验证码', max_length=4, min_length=4)

    def validate(self, attrs):
        # 获取图片验证码标识和用户输入的图片验证码内容
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 根据'image_code_id'从redis中获取真实的图片验证码文本
        redis_con = get_redis_connection('verify_codes')
        real_image_code = redis_con.get("img_%s" % image_code_id)

        # 生成的图片验证码只能使用一次,顾从redis中取出后当即删除,
        # 出错之后不再处理
        try:
            redis_con.delete("img_%s" % image_code_id)
        except Exception:
            pass



        if not real_image_code:
            raise serializers.ValidationError('图片验证码无效')

        # 对比图片验证码
        if text.lower() != real_image_code.decode().lower():
            raise serializers.ValidationError('图片验证失败')

        return attrs
