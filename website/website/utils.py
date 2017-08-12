from django.db import IntegrityError
from django.db.models.fields.related import OneToOneField, ReverseOneToOneDescriptor


def init_alerts():
    return {
        'error': [],
        'warning': [],
        'success': [],
        'info': [],
    }


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

