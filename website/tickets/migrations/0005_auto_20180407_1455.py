# Generated by Django 2.0.2 on 2018-04-07 13:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0010_auto_20180407_1455'),
        ('tickets', '0004_auto_20180228_0924'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['performance']},
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='box_office',
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='date_time',
        ),
        migrations.AddField(
            model_name='ticket',
            name='box_office_sale',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='program.BoxOfficeSale'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to=settings.AUTH_USER_MODEL),
        ),
    ]
