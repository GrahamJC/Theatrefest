# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-11 08:27
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import website.utils


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_auto_20170810_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 11, 9, 27, 44, 981931)),
        ),
        migrations.AlterField(
            model_name='basket',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 11, 9, 27, 44, 981931)),
        ),
        migrations.AlterField(
            model_name='basket',
            name='user',
            field=website.utils.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='basket', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='fringer',
            name='basket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fringers', to='tickets.Basket'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='basket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='tickets.Basket'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='fringer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='tickets.Fringer'),
        ),
    ]
