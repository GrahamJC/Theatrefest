# Generated by Django 2.0.5 on 2018-06-08 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_survey',
            field=models.BooleanField(default=False, help_text='Designates whether this user can be surveyed by e-mail.', verbose_name='e-mail survey'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name='last name'),
        ),
    ]
