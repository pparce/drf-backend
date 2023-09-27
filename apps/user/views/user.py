from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

from api.utils import Utils
from apps.user.models.user import User
from apps.user.serializers.user import UserSerializer, UserEditSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]

    def create(self, request):
        try:
            with transaction.atomic():
                user = User.objects.filter(
                    email=request.data.get("email", None))
                if user.count() > 0:
                    return Response(
                        {"message": "Este correo ya esta en uso"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                user.set_password(user.password)
                user.save()
                return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = User.objects.get(id=kwargs["pk"])
                serializer = UserEditSerializer(
                    data=request.data, instance=instance, partial=True
                )
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def admin_create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                user = User.objects.filter(
                    is_staff=True,
                    email=request.data.get("email", None))
                if user.count() > 0:
                    return Response(
                        {"message": "Este correo ya esta en uso"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user = User.objects.filter(
                    is_staff=False,
                    email=request.data.get("email", None))
                if user.count() > 0:
                    user_aux = User.objects.get(
                        email=request.data.get('email', None))
                    user_aux.is_staff = True
                    user_aux.save()
                    return Response(UserSerializer(user_aux).data)
                else:
                    serializer = self.serializer_class(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    user = serializer.save()
                    user.set_password(user.password)
                    user.save()
                    return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        serializer = AuthTokenSerializer()
        try:
            serializer: AuthTokenSerializer = AuthTokenSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            user.set_password(request.data.get("new_password", None))
            user.save()
            return Response(
                {
                    "message": "La contraseña se ha cambiado satisfactoriamente",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "message": "Contraseña incorrecta. Revise los datos introducidos",
                    "errors": serializer.errors,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


