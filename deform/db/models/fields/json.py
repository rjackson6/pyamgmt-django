__all__ = ['JSONField']

import django.db.models.fields.json

from deform import forms
from deform.db.models.fields.fields import Field


class JSONField(django.db.models.fields.json.JSONField, Field):
    """Override formfield() method"""
    def formfield(self, **kwargs):
        # return super().formfield(**{
        return Field.formfield(self, **{
            'form_class': forms.JSONField,
            'encoder': self.encoder,
            'decoder': self.decoder,
            **kwargs,
        })
