# Generated by Django 2.0.2 on 2018-02-24 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='uploads/program/company/'),
        ),
        migrations.AlterField(
            model_name='show',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='uploads/program/show/'),
        ),
        migrations.AlterField(
            model_name='venue',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='uploads/program/venue/'),
        ),
    ]