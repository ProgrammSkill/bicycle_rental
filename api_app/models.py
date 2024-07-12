from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=150, unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    surname = models.CharField(max_length=150, blank=True, null=True)
    patronymic = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False, null=True)
    is_superuser = models.BooleanField(default=0, null=True)
    is_active = models.BooleanField(default=1, null=True)
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.email


class Bicycle(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented'),
    )

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.name


class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bicycle = models.ForeignKey(Bicycle, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} rented {self.bicycle.name}'