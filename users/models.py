from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendedor'),
        ('customer', 'Cliente'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    email = models.EmailField(unique=True)

    def is_vendor(self):
        return self.user_type == 'vendor'