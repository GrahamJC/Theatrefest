# Generated by Django 2.0.4 on 2018-04-08 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_auto_20180407_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='tickettype',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
