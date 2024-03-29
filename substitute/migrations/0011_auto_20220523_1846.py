# Generated by Django 3.1.7 on 2022-05-23 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('substitute', '0010_auto_20220512_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='end',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='start',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='day',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='period',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
