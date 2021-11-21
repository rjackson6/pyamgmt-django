import django.forms.fields

from deform.forms.boundfield import BoundField


class Field(django.forms.fields.Field):
    """Custom Field class to override get_bound_field() class."""
    def get_bound_field(self, form, field_name):
        return BoundField(form, self, field_name)


class CharField(django.forms.fields.CharField, Field):
    pass


class IntegerField(django.forms.fields.IntegerField, Field):
    pass


class FloatField(django.forms.fields.FloatField, IntegerField):
    pass


class DecimalField(django.forms.fields.DecimalField, IntegerField):
    pass


class BaseTemporalField(django.forms.fields.BaseTemporalField, Field):
    pass


class DateField(django.forms.fields.DateField, BaseTemporalField):
    pass


class TimeField(django.forms.fields.TimeField, BaseTemporalField):
    pass


# class DateTimeFormatsIterator


class DateTimeField(django.forms.fields.DateTimeField, BaseTemporalField):
    pass


class DurationField(django.forms.fields.DurationField, Field):
    pass


class RegexField(django.forms.fields.RegexField, CharField):
    pass


class EmailField(django.forms.fields.EmailField, CharField):
    pass


class FileField(django.forms.fields.FileField, Field):
    pass


class ImageField(django.forms.fields.ImageField, FileField):
    pass


class URLField(django.forms.fields.URLField, CharField):
    pass


class BooleanField(django.forms.fields.BooleanField, Field):
    pass


class NullBooleanField(django.forms.fields.NullBooleanField, BooleanField):
    pass


# class CallableChoiceIterator


class ChoiceField(django.forms.fields.ChoiceField, Field):
    pass


class TypedChoiceField(django.forms.fields.TypedChoiceField, ChoiceField):
    pass


class MultipleChoiceField(django.forms.fields.MultipleChoiceField, ChoiceField):
    pass


class TypedMultipleChoiceField(django.forms.fields.TypedMultipleChoiceField, MultipleChoiceField):
    pass


class ComboField(django.forms.fields.ComboField, Field):
    pass


class MultiValueField(django.forms.fields.MultiValueField, Field):
    pass


class FilePathField(django.forms.fields.FilePathField, ChoiceField):
    pass


class SplitDateTimeField(django.forms.fields.SplitDateTimeField, MultiValueField):
    pass


class GenericIPAddressField(django.forms.fields.GenericIPAddressField, CharField):
    pass


class SlugField(django.forms.fields.SlugField, CharField):
    pass


class UUIDField(django.forms.fields.UUIDField, CharField):
    pass


# class InvalidJSONInput
# class JSONString


class JSONField(django.forms.fields.JSONField, CharField):
    pass
