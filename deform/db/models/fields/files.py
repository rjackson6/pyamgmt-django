import django.db.models.fields.files

from deform import forms
from deform.db.models.fields.fields import Field


class FileField(django.db.models.fields.files.FileField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.FileField,
            'max_length': self.max_length,
            **kwargs,
        })


class ImageField(django.db.models.fields.files.ImageField, FileField):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return FileField.formfield(self, **{
            'form_class': forms.ImageField,
            **kwargs,
        })
