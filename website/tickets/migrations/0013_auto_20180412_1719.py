# Generated by Django 2.0.4 on 2018-04-12 16:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0012_auto_20180412_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fringer',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fringers', to=settings.AUTH_USER_MODEL),
        ),
    ]
