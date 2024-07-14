from django.urls import include, path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from api_app.views import AuthView, AccountCreateAPIView, RefreshView, BicycleListAPIView, RentalCreateAPIView, \
    ReturnBicycleCreateAPIView, RentalHistoryAPIView

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('auth/', AuthView.as_view()),
    path('create-account/', AccountCreateAPIView.as_view()),
    path('refresh-token/', RefreshView.as_view()),
    path('bicycles/', BicycleListAPIView.as_view(), name='bicycle-list'),
    path('rental-history/', RentalHistoryAPIView.as_view(), name='rental-history'),
    path('rentals/', RentalCreateAPIView.as_view(), name='rental-create'),
    path('return-bicycle/<int:rental_id>', ReturnBicycleCreateAPIView.as_view(), name='return-bicycle'),


]
