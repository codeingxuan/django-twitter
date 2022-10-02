# 如何序列化数据，转换为json格式
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        # 中括号改成了大括号
        fields = ('url', 'username', 'email')