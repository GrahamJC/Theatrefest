# Generated by Django 2.0.4 on 2018-05-27 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0015_auto_20180414_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='stripe_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=4),
        ),
    ]
