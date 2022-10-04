from accounts.api.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from accounts.api.serializers import SignupSerializer, LoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # 大概是类似于数据从哪里获得的，本来应该是sql语句
    queryset = User.objects.all().order_by('-date_joined')
    # 序列类型，参照序列构造的类 serialize，定义了数据构建的形式
    serializer_class = UserSerializer
    # 权限的参数，这里的意思是必须要是授权用户才可以发这个请求
    permission_classes = (permissions.IsAuthenticated,)

# 白名单模式
class AccountViewSet(viewsets.ViewSet):
    permissions_classes = (AllowAny, )
    # 可以获得构造序列
    serializer_class = SignupSerializer
    # action可以控制一些api的参数，methods指定了哪些是可以的，detail=False表示这个请求可以不用带id，不是对象接口，是普通接口，直接访问url
    @action(methods=['POST'], detail=False)
    def login(self, request):
        """
        默认的 username 是 admin, password 也是 admin
        """
        # 序列构造器，进行格式渲染和解析，request.data是用户传过来的数据，是json格式，放入构造器中进行格式转换
        serializer = LoginSerializer(data=request.data)
        # 提取到了空字符串，意味着用户没用输入
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # authenticate 是 django的contrib.auth库中的验证授权的函数，可以验证用户名和密码是否正确，内部提供了密码加密机制
        # 这里引入包的时候重命名了为django_authenticate
        user = django_authenticate(username=username, password=password)
        # 如果不存在用户或用户密码错误
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match",
            }, status=400)
        # django登录函数，cookie生成令牌
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """
        登出当前用户
        """
        django_logout(request)
        return Response({"success": True})

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """
        使用 username, email, password 进行注册
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input!",
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        })

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        查看用户当前的登录状态和具体信息
        """
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data

        # Response默认的状态码是200
        return Response(data)