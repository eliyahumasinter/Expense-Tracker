from django.db import models
from django.utils import timezone
from users.models import Profile


class Entry(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    date_posted = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField('EntryTag', blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class EntryTag(models.Model):
    tag = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    def __str__(self):
        return self.tag
