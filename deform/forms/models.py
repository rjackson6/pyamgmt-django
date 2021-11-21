__all__ = (
    'BaseModelForm', 'BaseInlineFormSet',
    'ModelChoiceField', 'ModelForm', 'ModelMultipleChoiceField',
    'inlineformset_factory'
)

import django.forms.models
from django.forms.utils import ErrorList
from django.forms.widgets import HiddenInput
from django.utils.text import capfirst

from deform.forms.fields import ChoiceField, Field
from deform.forms.forms import BaseForm
from deform.forms.formsets import BaseFormSet


class BaseModelForm(django.forms.BaseModelForm, BaseForm):
    """Override of BaseModelForm
    Method resolution order with (django.forms.BaseModelForm, BaseForm):
        BaseModelForm
        django.forms.models.BaseModelForm
        deform.forms.forms.BaseForm
        django.forms.forms.BaseForm
        builtins.object
    """
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(
            data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial, error_class=error_class,
            label_suffix=label_suffix, empty_permitted=empty_permitted, instance=instance,
            use_required_attribute=use_required_attribute, renderer=renderer
        )


class ModelForm(django.forms.ModelForm, BaseModelForm):
    """Override of ModelForm
    Method resolution order with (django.forms.ModelForm, BaseModelForm):
        ModelForm
        django.forms.models.ModelForm
        BaseModelForm
        django.forms.models.BaseModelForm
        deform.forms.forms.BaseForm
        django.forms.forms.BaseForm
        builtins.object
    """


def modelform_factory(model, form=ModelForm, **kwargs):
    return django.forms.models.modelform_factory(model, form=form, **kwargs)


# noinspection PyProtectedMember
class BaseModelFormSet(django.forms.models.BaseModelFormSet, BaseFormSet):
    def add_fields(self, form, index):
        """Override of Django method.
        Add a hidden field for the object's primary key.
        """
        from django.db.models import AutoField, ForeignKey, OneToOneField
        self._pk_field = pk = self.model._meta.pk  # noqa

        # If a pk isn't editable, then it won't be on the form, so we need to
        # add it here so we can tell which object is which when we get the
        # data back. Generally, pk.editable should be false, but for some
        # reason, auto_created pk fields and AutoField's editable attribute is
        # True, so check for that as well.

        def pk_is_not_editable(pk):  # noqa
            return (
                (not pk.editable) or (pk.auto_created or isinstance(pk, AutoField)) or (
                    pk.remote_field and pk.remote_field.parent_link and
                    pk_is_not_editable(pk.remote_field.model._meta.pk)
                )
            )

        if pk_is_not_editable(pk) or pk.name not in form.fields:
            if form.is_bound:
                # If we're adding the related instance, ignore its primary key
                # as it could be an auto-generated default which isn't actually
                # in the database.
                pk_value = None if form.instance._state.adding else form.instance.pk
            else:
                try:
                    if index is not None:
                        pk_value = self.get_queryset()[index].pk
                    else:
                        pk_value = None
                except IndexError:
                    pk_value = None
            if isinstance(pk, (ForeignKey, OneToOneField)):
                qs = pk.remote_field.model._default_manager.get_queryset()
            else:
                qs = self.model._default_manager.get_queryset()
            qs = qs.using(form.instance._state.db)
            if form._meta.widgets:
                widget = form._meta.widgets.get(self._pk_field.name, HiddenInput)
            else:
                widget = HiddenInput
            form.fields[self._pk_field.name] = ModelChoiceField(qs, initial=pk_value, required=False, widget=widget)
        BaseFormSet.add_fields(self, form, index)


def modelformset_factory(model, form=ModelForm, formset=BaseModelFormSet, **kwargs):
    return django.forms.models.modelformset_factory(model, form=form, formset=formset, **kwargs)


# noinspection PyProtectedMember
class BaseInlineFormSet(django.forms.models.BaseInlineFormSet, BaseModelFormSet):
    def add_fields(self, form, index):
        """Overrides InlineForeignKeyField Class"""
        BaseModelFormSet.add_fields(self, form, index)
        if self._pk_field == self.fk:
            name = self._pk_field.name
            kwargs = {'pk_field': True}
        else:
            # The foreign key field might not be on the form, so we poke at the
            # Model field to get the label, since we need that for error messages.
            name = self.fk.name
            kwargs = {
                'label': getattr(form.fields.get(name), 'label', capfirst(self.fk.verbose_name))
            }

        # The InlineForeignKeyField assumes that the foreign key relation is
        # based on the parent model's pk. If this isn't the case, set to_field
        # to correctly resolve the initial form value.
        if self.fk.remote_field.field_name != self.fk.remote_field.model._meta.pk.name:
            kwargs['to_field'] = self.fk.remote_field.field_name

        # If we're adding a new object, ignore a parent's auto-generated key
        # as it will be regenerated on the save request.
        if self.instance._state.adding:
            if kwargs.get('to_field') is not None:
                to_field = self.instance._meta.get_field(kwargs['to_field'])
            else:
                to_field = self.instance._meta.pk
            if to_field.has_default():
                setattr(self.instance, to_field.attname, None)

        form.fields[name] = InlineForeignKeyField(self.instance, **kwargs)


# noinspection PyProtectedMember
def _get_foreign_key(parent_model, model, fk_name=None, can_fail=False):
    """
    Find and return the ForeignKey from model to parent if there is one
    (return None if can_fail is True and no such field exists). If fk_name is
    provided, assume it is the name of the ForeignKey field. Unless can_fail is
    True, raise an exception if there isn't a ForeignKey from model to
    parent_model.
    """
    # avoid circular import
    from deform.db.models.fields import ForeignKey
    opts = model._meta
    if fk_name:
        fks_to_parent = [f for f in opts.fields if f.name == fk_name]
        if len(fks_to_parent) == 1:
            fk = fks_to_parent[0]
            if not isinstance(fk, ForeignKey) or \
                    (fk.remote_field.model != parent_model and
                     fk.remote_field.model not in parent_model._meta.get_parent_list()):
                raise ValueError(
                    "fk_name '%s' is not a ForeignKey to '%s'." % (fk_name, parent_model._meta.label)
                )
        elif not fks_to_parent:
            raise ValueError(
                "'%s' has no field named '%s'." % (model._meta.label, fk_name)
            )
    else:
        # Try to discover what the ForeignKey from model to parent_model is
        fks_to_parent = [
            f for f in opts.fields
            if isinstance(f, ForeignKey) and (
                f.remote_field.model == parent_model or
                f.remote_field.model in parent_model._meta.get_parent_list()
            )
        ]
        if len(fks_to_parent) == 1:
            fk = fks_to_parent[0]
        elif not fks_to_parent:
            if can_fail:
                return
            raise ValueError(
                "'%s' has no ForeignKey to '%s'." % (
                    model._meta.label,
                    parent_model._meta.label,
                )
            )
        else:
            raise ValueError(
                "'%s' has more than one ForeignKey to '%s'. You must specify "
                "a 'fk_name' attribute." % (
                    model._meta.label,
                    parent_model._meta.label,
                )
            )
    return fk  # noqa


def inlineformset_factory(parent_model, model, form=ModelForm,
                          formset=BaseInlineFormSet, fk_name=None,
                          fields=None, exclude=None, extra=3, can_order=False,
                          can_delete=True, max_num=None, formfield_callback=None,
                          widgets=None, validate_max=False, localized_fields=None,
                          labels=None, help_texts=None, error_messages=None,
                          min_num=None, validate_min=False, field_classes=None,
                          absolute_max=None, can_delete_extra=True):
    """
    Complete override of Django function.

    Return an ``InlineFormSet`` for the given kwargs.

    ``fk_name`` must be provided if ``model`` has more than one ``ForeignKey``
    to ``parent_model``.
    """
    fk = _get_foreign_key(parent_model, model, fk_name=fk_name)
    # enforce a max_num=1 when the foreign key to the parent model is unique.
    if fk.unique:
        max_num = 1
    kwargs = {
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': formset,
        'extra': extra,
        'can_delete': can_delete,
        'can_order': can_order,
        'fields': fields,
        'exclude': exclude,
        'min_num': min_num,
        'max_num': max_num,
        'widgets': widgets,
        'validate_min': validate_min,
        'validate_max': validate_max,
        'localized_fields': localized_fields,
        'labels': labels,
        'help_texts': help_texts,
        'error_messages': error_messages,
        'field_classes': field_classes,
        'absolute_max': absolute_max,
        'can_delete_extra': can_delete_extra,
    }
    FormSet = modelformset_factory(model, **kwargs)  # noqa
    FormSet.fk = fk
    return FormSet


class InlineForeignKeyField(django.forms.models.InlineForeignKeyField, Field):
    pass


# ModelChoiceIteratorValue
# ModelChoiceIterator


class ModelChoiceField(django.forms.models.ModelChoiceField, ChoiceField):
    pass


class ModelMultipleChoiceField(django.forms.models.ModelMultipleChoiceField, ModelChoiceField):
    pass
