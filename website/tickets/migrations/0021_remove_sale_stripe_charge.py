# Generated by Django 2.0.5 on 2018-06-16 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0020_sale_stripe_fee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='stripe_charge',
        ),
    ]
