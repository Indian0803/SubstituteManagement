# Generated by Django 4.0.4 on 2022-05-24 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('substitute', '0012_remove_user_schedule_uploaded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='period',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
