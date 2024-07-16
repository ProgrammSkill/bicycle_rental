from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from api_app.serializers import AccountCreateSerializer


auth = extend_schema_view(
    post=extend_schema(
        summary="Авторизация",
        tags=['Sign in and sign up'],
        request=inline_serializer('auth_request', {
            'email': serializers.CharField(),
            'password': serializers.CharField()
        }),
        responses={
            '200': inline_serializer('auth_response2', {
                'access': serializers.CharField(),
                'refresh': serializers.CharField()
            })
        }
    )
)

create = extend_schema_view(
    post=extend_schema(
        summary="Регистрация",
        tags=['Sign in and sign up'],
        responses={
            '200': inline_serializer('user_create_response', {
                'access': serializers.CharField(),
                'refresh': serializers.CharField(),
                'user': AccountCreateSerializer()
            })
        }
    )
)

refresh = extend_schema_view(
    post=extend_schema(
        summary="Обновить токен",
        tags=['Sign in and sign up']
    )
)