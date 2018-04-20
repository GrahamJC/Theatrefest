# Generated by Django 2.0.2 on 2018-04-07 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0010_auto_20180407_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='boxofficesale',
            name='completed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='boxofficesale',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='sales', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
