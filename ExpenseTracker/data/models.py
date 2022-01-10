from django.db import models
from django.utils import timezone


class Entry(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    date_posted = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField('EntryTag', blank=True)

    def __str__(self):
        return self.title


class EntryTag(models.Model):
    tag = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.tag
