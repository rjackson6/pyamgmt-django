import django.db.models
from django import template
from django.utils.datastructures import ImmutableList
from django.utils.safestring import mark_safe

register = template.Library()


def doc(obj) -> str:
    if obj == '':
        return mark_safe('<!-- no obj -->')
    if not hasattr(obj, '__doc__'):
        return mark_safe('<!-- no doc -->')
    if hasattr(obj, '__bases__'):
        this = [f'{obj.__name__}: {obj.__doc__}']
        bases = [f'{x.__name__}: {x.__doc__}' for x in obj.__bases__ if hasattr(x, '__doc__')]
        return '\n\n'.join(this + bases)
    return obj.__doc__


def fields(obj: django.db.models.Model) -> ImmutableList:
    return obj._meta.get_fields()


def name_(obj):
    return str(getattr(obj, '__name__', ''))


register.filter('doc', doc)
register.filter('fields', fields)
register.filter('name', name_)
