from django.db import connection
import django.db.models.fields
import django.forms.widgets
from django.utils.text import capfirst

from deform import forms


__all__ = [
    'BigIntegerField', 'BinaryField', 'BooleanField',
    'CharField', 'CommaSeparatedIntegerField',
    'DateField', 'DateTimeField', 'DecimalField', 'DurationField',
    'EmailField',
    'Field', 'FilePathField', 'FloatField',
    'GenericIPAddressField',
    'IntegerField', 'IPAddressField',
    'PositiveBigIntegerField', 'PositiveIntegerField', 'PositiveSmallIntegerField',
    'SlugField', 'SmallIntegerField',
    'TextField', 'TimeField',
    'URLField', 'UUIDField'
]


class Field(django.db.models.fields.Field):
    """Custom implementation of Field to support form classes."""
    def formfield(self, form_class=None, choices_form_class=None, **kwargs):
        """Return a deform.forms.fields.Field instance for this field."""
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
        }
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()
        if self.choices is not None:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
                             not (self.has_default() or 'initial' in kwargs))
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = None
            if choices_form_class is not None:
                form_class = choices_form_class
            else:
                form_class = forms.TypedChoiceField
            # Many of the subclass-specific formfield arguments (min_value,
            # max_value) don't apply for choice fields, so be sure to only pass
            # the values that TypedChoiceField will understand.
            for k in list(kwargs):
                if k not in ('coerce', 'empty_value', 'choices', 'required',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial', 'disabled'):
                    del kwargs[k]
        defaults.update(kwargs)
        if form_class is None:
            form_class = forms.CharField
        return form_class(**defaults)


class BooleanField(django.db.models.fields.BooleanField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        if self.choices is not None:
            include_blank = not (self.has_default() or 'initial' in kwargs)
            defaults = {'choices': self.get_choices(include_blank=include_blank)}
        else:
            form_class = forms.NullBooleanField if self.null else forms.BooleanField
            defaults = {'form_class': form_class, 'required': False}
        # return super().formfield(**{**defaults, **kwargs})
        return Field.formfield(self, **{**defaults, **kwargs})


class CharField(django.db.models.fields.CharField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        """formfield() doesn't specify a form_class"""
        defaults = {'max_length': self.max_length}
        if self.null and not connection.features.interprets_empty_strings_as_nulls:
            defaults['empty_value'] = None
        defaults.update(kwargs)
        # return super().formfield(**defaults)
        return Field.formfield(self, **defaults)


class CommaSeparatedIntegerField(django.db.models.fields.CommaSeparatedIntegerField, CharField):
    pass


class DateField(django.db.models.fields.DateField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.DateField,
            **kwargs,
        })


class DateTimeField(django.db.models.fields.DateTimeField, DateField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return DateField.formfield(self, **{
            'form_class': forms.DateTimeField,
            **kwargs,
        })


class DecimalField(django.db.models.fields.DecimalField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'max_digits': self.max_digits,
            'decimal_places': self.decimal_places,
            'form_class': forms.DecimalField,
            **kwargs,
        })


class DurationField(django.db.models.fields.DurationField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.DurationField,
            **kwargs,
        })


class EmailField(django.db.models.fields.EmailField, CharField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return CharField.formfield(self, **{
            'form_class': forms.EmailField,
            **kwargs,
        })


class FilePathField(django.db.models.fields.FilePathField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'path': self.path() if callable(self.path) else self.path,
            'match': self.match,
            'recursive': self.recursive,
            'form_class': forms.FilePathField,
            'allow_files': self.allow_files,
            'allow_folders': self.allow_folders,
            **kwargs,
        })


class FloatField(django.db.models.fields.FloatField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.FloatField,
            **kwargs,
        })


class IntegerField(django.db.models.fields.IntegerField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.IntegerField,
            **kwargs,
        })


class BigIntegerField(django.db.models.fields.BigIntegerField, IntegerField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return IntegerField.formfield(self, **{
            'min_value': -BigIntegerField.MAX_BIGINT - 1,
            'max_value': BigIntegerField.MAX_BIGINT,
            **kwargs,
        })


class SmallIntegerField(django.db.models.fields.SmallIntegerField, IntegerField):
    """No native formfield() method"""
    def formfield(self, **kwargs):
        return IntegerField.formfield(self, **kwargs)


class IPAddressField(django.db.models.fields.IPAddressField, Field):
    """No native formfield() method"""
    def formfield(self, **kwargs):
        return Field.formfield(self, **kwargs)


class GenericIPAddressField(django.db.models.fields.GenericIPAddressField, Field):
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'protocol': self.protocol,
            'form_class': forms.GenericIPAddressField,
            **kwargs,
        })


class NullBooleanField(django.db.models.fields.NullBooleanField, BooleanField):
    """Deprecated; no formfield() method"""


class PositiveBigIntegerField(django.db.models.fields.PositiveBigIntegerField, BigIntegerField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        """formfield() doesn't specify a class"""
        # return super().formfield(**{
        return BigIntegerField.formfield(self, **{
            'min_value': 0,
            **kwargs,
        })


class PositiveIntegerField(django.db.models.fields.PositiveIntegerField, IntegerField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        """formfield() doesn't specify a class"""
        # return super().formfield(**{
        return IntegerField.formfield(self, **{
            'min_value': 0,
            **kwargs,
        })


class PositiveSmallIntegerField(django.db.models.fields.PositiveSmallIntegerField, SmallIntegerField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        """formfield() doesn't specify a class"""
        # return super().formfield(**{
        return SmallIntegerField.formfield(self, **{
            'min_value': 0,
            **kwargs,
        })


class SlugField(django.db.models.fields.SlugField, CharField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return CharField.formfield(self, **{
            'form_class': forms.SlugField,
            'allow_unicode': self.allow_unicode,
            **kwargs,
        })


class TextField(django.db.models.fields.TextField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        """formfield() specifies a widget, but not a field class"""
        # return super().formfield(**{
        return Field.formfield(self, **{
            'max_length': self.max_length,
            **({} if self.choices is not None else {'widget': django.forms.widgets.Textarea}),
            **kwargs,
        })


class TimeField(django.db.models.fields.TimeField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.TimeField,
            **kwargs,
        })


class URLField(django.db.models.fields.URLField, CharField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return CharField.formfield(self, **{
            'form_class': forms.URLField,
            **kwargs,
        })


class BinaryField(django.db.models.fields.BinaryField, Field):
    """No native formfield() method"""
    def formfield(self, **kwargs):
        return Field.formfield(self, **kwargs)


class UUIDField(django.db.models.fields.UUIDField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.UUIDField,
            **kwargs,
        })


# class AutoFieldMixin  - formfield() returns None
