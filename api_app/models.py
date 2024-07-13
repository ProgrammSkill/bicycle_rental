from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=150)
    fullname = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.BooleanField(default=False, null=True)
    is_superuser = models.BooleanField(default=0, null=True)
    is_active = models.BooleanField(default=1, null=True)
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class UserOutstandingToken(OutstandingToken):
    DEVICES_IDS = [
        [0, "Desktop"],
        [1, "Android"],
        [2, "iOS"],
        [3, "Mobile WEB"],
        [4, "DWED infomat"],
        [5, "TMED"],
    ]

    device_id = models.IntegerField(choices=DEVICES_IDS, default=0)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=128, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, to_field='email')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'token_blacklist_outstandingtoken'


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