# Generated by Django 2.0.2 on 2018-02-28 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0005_auto_20180225_1806'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoxOffice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=32, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
