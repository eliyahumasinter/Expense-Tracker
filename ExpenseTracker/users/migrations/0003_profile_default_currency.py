# Generated by Django 4.0.1 on 2022-01-30 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_profile_name_profile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_currency',
            field=models.CharField(default='USD', max_length=3),
        ),
    ]
