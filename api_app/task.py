from celery import shared_task
from django.utils import timezone
from api_app.models import Rental


@shared_task
def calculate_rental_cost(rental_id):
    rental = Rental.objects.get(pk=rental_id)

    start_time = rental.start_time
    end_time = timezone.now()
    duration = end_time - start_time

    cost_per_minute = 2  # Цена за 1 минуту

    cost = round(duration.total_seconds() / 60 * cost_per_minute, 2)

    return cost
