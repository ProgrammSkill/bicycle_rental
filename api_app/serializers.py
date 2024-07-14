from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import ValidationError
from api_app.common_utils.token import get_token
from api_app.models import User, Bicycle, Rental
from rest_framework import serializers
from django.utils import timezone


class AuthSerializer(serializers.Serializer):
    """ Сериалайзер для авторизации пользователя """
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    redirect_url = serializers.CharField(read_only=True)

    @staticmethod
    def _get_user(validated_data):
        return User.objects.get(email=validated_data['email'])

    def validate(self, attrs):
        try:
            user = self._get_user(attrs)
            if not check_password(attrs.get('password'), user.password):
                raise ValidationError({'message': 'Логин или пароль неверный'})
        except User.DoesNotExist:
            raise ValidationError({'message': 'Логин или пароль неверный'})
        return attrs

    def validate(self, attrs):
        try:
            user = self._get_user(attrs)
            if not check_password(attrs.get('password'), user.password):
                raise ValidationError({'message': 'Логин или пароль неверный'})
        except User.DoesNotExist:
            raise ValidationError({'message': 'Логин или пароль неверный'})
        return attrs

    def create(self, validated_data):
        try:
            user = self._get_user(validated_data)
            token = get_token(self.context['request'], user)
            return {
                'access': str(token.access_token),
                'refresh': str(token)
            }
        except User.DoesNotExist:
            return {
                'redirect_url': f"{self.context['request'].scheme}://{self.context['request'].get_host()}"
                                f"/api_app/auth_user/"
            }


class AccountCreateSerializer(serializers.ModelSerializer):
    """ Сериалайзер для регистрации пользователя """
    email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    verified_password = serializers.CharField(write_only=True, required=True)
    fullname = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'verified_password',
            'fullname',
        )
        write_only_fields = ('password', 'verified_password')

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise ValidationError({'email': 'Почта занята другим пользователем'})
        return value

    @staticmethod
    def validate_password(value):
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise ValidationError({'password': e})
        return value

    def create(self, validated_data):
        if validated_data['verified_password'] != validated_data['password']:
            raise ValidationError({'verified_password': 'Пароли не совпадают'})

        validated_data.pop('verified_password')
        instance: User = super(AccountCreateSerializer, self).create(validated_data)
        # хэширование пароля
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class BicycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bicycle
        fields = '__all__'


class RentalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rental
        fields = ('id', 'user', 'bicycle', 'start_time')

    def validate(self, data):
        # Проверка, что пользователь уже не арендует другой велосипед
        user_rentals = Rental.objects.filter(user=data['user'], end_time__isnull=True)
        if user_rentals.exists():
            raise serializers.ValidationError("Вы уже арендуете другой велосипед.")

        # Проверка, что выбранный велосипед доступен для аренды
        if data['bicycle'].status == 'rented':
            raise serializers.ValidationError("Выбранный велосипед уже арендован.")

        return data

    def create(self, validated_data):
        bicycle = Bicycle.objects.get(pk=validated_data['bicycle'].id)
        bicycle.status = 'rented'
        bicycle.save()

        instance: Rental = super(RentalSerializer, self).create(validated_data)
        instance.save()
        return instance
