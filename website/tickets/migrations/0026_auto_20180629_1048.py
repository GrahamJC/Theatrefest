# Generated by Django 2.0.5 on 2018-06-29 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0025_auto_20180629_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='fringer',
            name='payment',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=4),
        ),
        migrations.AddField(
            model_name='fringertype',
            name='payment',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=4),
        ),
    ]
