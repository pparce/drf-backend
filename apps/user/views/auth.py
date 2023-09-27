from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from api.utils import Utils
from apps.user.models.user import User
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db import transaction
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.serializers.user import UserSerializer


class AuthViewSet(viewsets.ViewSet):
    serializer_class = AuthTokenSerializer
    @action(detail=False, methods=['post'])
    def login(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer()
        try:
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            user.restore_code = None
            user.save()
            return Response({
                'token': str(refresh.access_token),
                'token_refresh': str(refresh),
                'user': UserSerializer(user).data,
            })
        except Exception as e:
            return Response({
                'message': 'Wrong username or password. Check the data entered',
                'errors': serializer.errors
            }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def sending_restore_code(self, request):
        try:
            user = User.objects.get(email=request.data.get('email', None))
            user.restore_code = Utils().generar_codigo()
            user.save()
            text_content = f''' 
              <span style="color: rgb(0, 0, 0); font-family: &quot;Times New Roman&quot;; font-size: medium;">Dear {user.first_name} {user.last_name},&nbsp;</span><div><font color="#000000" face="Times New Roman" size="3"><br></font><div><span style="color: rgb(0, 0, 0); font-family: &quot;Times New Roman&quot;; font-size: medium;">We are sending you this email in response to your password reset request.&nbsp;</span></div><div><span style="color: rgb(0, 0, 0); font-family: &quot;Times New Roman&quot;;"><font size="3">Your verification code is </font><b style=""><font size="4">{user.restore_code}</font></b><font size="3">. Please enter this code on the password reset page to proceed with the password reset process. If you did not request a password reset, please ignore this message.</font></span></div><div><span style="color: rgb(0, 0, 0); font-family: &quot;Times New Roman&quot;;"><font size="3">Thank you.</font></span></div><div style="text-align: left;"><span style="color: rgb(0, 0, 0); font-family: &quot;Times New Roman&quot;;"><font size="3">ARTESSE PROJECT</font></span></div></div>
              '''
            # sendMail.delay({
            #     'subject': 'Restore password',
            #     'text_content': text_content,
            #     'to': request.data.get("email", None),
            #     'html_content': text_content
            # })
            return Response({
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': "Email does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def restore_password(self, request):
        try:
            user = User.objects.get(id=request.data.get('user_id', None))
            if str(user.restore_code) == str(request.data.get('code', None)):
                user.set_password(request.data.get("new_password", None))
                user.save()
                return Response()
            else:
                return Response({
                    'error': 'This code is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'error': "Email does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def register(self, request, *arg, **kwargs):
        try:
            with transaction.atomic():
                user = User.objects.filter(
                    email=request.data.get("email", None))
                if user.count() > 0:
                    return Response(
                        {"message": "This email is already in use"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer = UserSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                user.set_password(user.password)
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'token': str(refresh.access_token),
                    'token_refresh': str(refresh),
                    'user': UserSerializer(user).data,
                })
        except Exception as e:
            print(e)
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

