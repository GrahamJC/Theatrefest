# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 10:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='show',
            old_name='adult',
            new_name='adult_content',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='payment',
            new_name='payment_type',
        ),
        migrations.AddField(
            model_name='show',
            name='nudity',
            field=models.BooleanField(default=False),
        ),
    ]
