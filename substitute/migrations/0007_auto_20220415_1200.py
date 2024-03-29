# Generated by Django 3.1.2 on 2022-04-15 03:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('substitute', '0006_auto_20220413_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='substituteschedule',
            name='lunch_recess',
            field=models.ManyToManyField(blank=True, null=True, related_name='lunch_recess', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substituteschedule',
            name='morning_recess',
            field=models.ManyToManyField(blank=True, null=True, related_name='morning_recess', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substituteschedule',
            name='period_five',
            field=models.ManyToManyField(blank=True, null=True, related_name='period_five', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substituteschedule',
            name='period_four',
            field=models.ManyToManyField(blank=True, null=True, related_name='period_four', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substituteschedule',
            name='period_one',
            field=models.ManyToManyField(blank=True, null=True, related_name='period_one', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substituteschedule',
            name='period_six',
            field=models.ManyToManyField(blank=True, null=True, related_name='period_six', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substituteschedule',
            name='period_three',
            field=models.ManyToManyField(blank=True, null=True, related_name='period_three', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='substituteschedule',
            name='period_two',
            field=models.ManyToManyField(blank=True, null=True, related_name='period_two', to=settings.AUTH_USER_MODEL),
        ),
    ]
