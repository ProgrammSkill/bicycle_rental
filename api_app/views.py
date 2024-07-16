from datetime import datetime
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.transaction import atomic
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from api_app.common_utils.token import get_token
from api_app.serializers import AccountCreateSerializer, AuthSerializer, BicycleSerializer, RentalSerializer
from .models import User, Bicycle, Rental
from .common_utils.serializers import TokenRefreshSerializer
from .swagger_content import account, rental
from .task import calculate_rental_cost


@account.auth
class AuthView(CreateAPIView):
    serializer_class = AuthSerializer
    authentication_classes = ()
    permission_classes = ()


@account.create
class AccountCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AccountCreateSerializer
    authentication_classes = ()
    permission_classes = ()

    @atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Возвращается токен доступа для этого запроса и созданный пользовательский объект.
        token = get_token(request, serializer.instance)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


@account.refresh
class RefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@rental.bicycles
class BicycleListAPIView(generics.ListAPIView, generics.CreateAPIView):
    serializer_class = BicycleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Bicycle.objects.filter(status='available')
        return queryset


@rental.rent_bicycles
class RentalCreateAPIView(generics.CreateAPIView):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]


@rental.rental_history
class RentalHistoryAPIView(generics.ListAPIView):
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Rental.objects.filter(user=user)

        return queryset


@rental.return_bicycles
class ReturnBicycleCreateAPIView(generics.CreateAPIView):
    queryset = Rental.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, rental_id):
        user = self.request.user

        rentals = Rental.objects.filter(user=user,  bicycle__status='rented', end_time__isnull=True)
        if not rentals.exists():
            raise ValidationError("У вас нет арендованного велосипеда для возврата.")
        try:
            rental = Rental.objects.get(pk=rental_id)
            rental.end_time = datetime.now()
            # Запуск задачи Celery для расчета стоимости аренды
            rental.cost = calculate_rental_cost.delay(rental_id)
            Bicycle.objects.filter(pk=rental.bicycle.id).update(status='available')
            rental.save()

            return Response({'message': f'Велосипед успешно возвращен, сумма оплаты составляет: {rental.cost}'})
        except Rental.DoesNotExist:
            return Response({'error': 'Арендной платы не существует'}, status=404)
