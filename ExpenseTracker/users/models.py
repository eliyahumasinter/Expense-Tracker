from django.db import models
from django.contrib.auth.models import User



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=False)
    default_currency = models.CharField(max_length=3, default="USD")

    def __str__(self):
        return f'{self.user.username} Profile'
