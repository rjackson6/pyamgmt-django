import django.db.models
from django import template
from django.utils.datastructures import ImmutableList
from django.utils.safestring import mark_safe

register = template.Library()


def doc(obj):
    if obj == '':
        return mark_safe('<!-- no obj -->')
    return str(obj.__doc__)


def fields(obj: django.db.models.Model) -> ImmutableList:
    return obj._meta.get_fields()


register.filter('doc', doc)
register.filter('fields', fields)
