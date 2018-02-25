from django.db import models

from common.models import TimeStampedModel


class Image(models.Model):

    name = models.CharField(max_length = 32, unique = True)
    image = models.ImageField(upload_to = 'uploads/content/image/', blank = True, default = '')


class Page(models.Model):

    name = models.CharField(max_length = 32, unique = True)
    html = models.TextField(blank = True, default = '')
