from django.db import models

class TimeStampedModel(models.Model):

    """
    An abstract base class that provides self-updating 'created' and 'updated' fields.
    """

    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

