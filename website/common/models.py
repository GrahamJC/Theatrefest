from uuid import uuid4

from django.db import IntegrityError
from django.db import models
from django.db.models.fields.related import OneToOneField, ReverseOneToOneDescriptor

class TimeStampedModel(models.Model):

    """
    An abstract base class that provides self-updating 'created' and 'updated' fields.
    """

    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    uuid = models.UUIDField(unique = True, default = uuid4, editable = False)


class AutoSingleRelatedObjectDescriptor(ReverseOneToOneDescriptor):

    def __get__(self, instance, type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, type)
        except self.RelatedObjectDoesNotExist:
            kwargs = {
                self.related.field.name: instance,
            }
            rel_obj = self.related.related_model._default_manager.create(**kwargs)
            setattr(instance, self.cache_name, rel_obj)
            return rel_obj


class AutoOneToOneField(OneToOneField):

    related_accessor_class = AutoSingleRelatedObjectDescriptor

