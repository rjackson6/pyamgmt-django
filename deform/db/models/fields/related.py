import django.db.models.fields.related

from deform import forms
from deform.db.models.fields.fields import Field


class RelatedField(django.db.models.fields.related.RelatedField, Field):
    """Doesn't override form_class, but overrides formfield()."""
    def formfield(self, **kwargs):
        """Calls custom Field's method instead."""
        defaults = {}
        if hasattr(self.remote_field, 'get_related_field'):
            limit_choices_to = self.remote_field.limit_choices_to
            defaults.update({
                'limit_choices_to': limit_choices_to,
            })
        defaults.update(kwargs)
        # return super().formfield(**defaults)
        return Field.formfield(self, **defaults)


class ForeignObject(django.db.models.fields.related.ForeignObject, RelatedField):
    """No native formfield() method"""
    def formfield(self, **kwargs):
        return RelatedField.formfield(self, **kwargs)


# noinspection PyProtectedMember
class ForeignKey(django.db.models.fields.related.ForeignKey, ForeignObject):
    """Overrides formfield() and form_class"""
    def formfield(self, *, using=None, **kwargs):
        if isinstance(self.remote_field.model, str):
            raise ValueError("Cannot create form field for %r yet, because "
                             "its related model %r has not been loaded yet" %
                             (self.name, self.remote_field.model))
        # return super().formfield(**{
        return ForeignObject.formfield(self, **{
            'form_class': forms.ModelChoiceField,
            'queryset': self.remote_field.model._default_manager.using(using),
            'to_field_name': self.remote_field.field_name,
            **kwargs,
            'blank': self.blank,
        })


class OneToOneField(django.db.models.fields.related.OneToOneField, ForeignKey):
    """Doesn't override formclass, but overrides formfield()"""
    def formfield(self, **kwargs):
        """Returns custom ForeignKey.formfield() method."""
        if self.remote_field.parent_link:
            return None
        # return super().formfield(**kwargs)
        return ForeignKey.formfield(self, **kwargs)


# noinspection PyProtectedMember
class ManyToManyField(django.db.models.fields.related.ManyToManyField, RelatedField):
    """Overrides formfield() and form_class"""
    def formfield(self, *, using=None, **kwargs):
        defaults = {
            'form_class': forms.ModelMultipleChoiceField,
            'queryset': self.remote_field.model._default_manager.using(using),
            **kwargs
        }
        if defaults.get('initial') is not None:
            initial = defaults['initial']
            if callable(initial):
                initial = initial()
            defaults['initial'] = [i.pk for i in initial]
        # return super().formfield(**defaults)
        return RelatedField.formfield(self, **defaults)
