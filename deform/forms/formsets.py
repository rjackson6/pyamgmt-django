__all__ = ('BaseFormSet', 'formset_factory')

import django.forms.formsets
# noinspection PyProtectedMember
from django.forms.formsets import (
    TOTAL_FORM_COUNT,
    INITIAL_FORM_COUNT,
    MIN_NUM_FORM_COUNT,
    MAX_NUM_FORM_COUNT,
    ORDERING_FIELD_NAME,
    DELETION_FIELD_NAME
)
from django.forms.widgets import HiddenInput
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from deform.forms.fields import BooleanField, IntegerField
from deform.forms.forms import Form


class ManagementForm(django.forms.formsets.ManagementForm, Form):
    """
    Keep track of how many form instances are displayed on the page. If adding
    new forms via JavaScript, you should increment the count field of this form
    as well.
    """
    def __init__(self, *args, **kwargs):
        self.base_fields[TOTAL_FORM_COUNT] = IntegerField(widget=HiddenInput)
        self.base_fields[INITIAL_FORM_COUNT] = IntegerField(widget=HiddenInput)
        # MIN_NUM_FORM_COUNT and MAX_NUM_FORM_COUNT are output with the rest of
        # the management form, but only for the convenience of client-side
        # code. The POST value of them returned from the client is not checked.
        self.base_fields[MIN_NUM_FORM_COUNT] = IntegerField(required=False, widget=HiddenInput)
        self.base_fields[MAX_NUM_FORM_COUNT] = IntegerField(required=False, widget=HiddenInput)
        Form.__init__(self, *args, **kwargs)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     # When the management form is invalid, we don't know how many forms
    #     # were submitted.
    #     cleaned_data.setdefault(TOTAL_FORM_COUNT, 0)
    #     cleaned_data.setdefault(INITIAL_FORM_COUNT, 0)
    #     return cleaned_data


class BaseFormSet(django.forms.formsets.BaseFormSet):
    @cached_property
    def management_form(self):
        """Return the ManagementForm instance for this FormSet."""
        if self.is_bound:
            form = ManagementForm(self.data, auto_id=self.auto_id, prefix=self.prefix)
            form.full_clean()
        else:
            form = ManagementForm(auto_id=self.auto_id, prefix=self.prefix, initial={
                TOTAL_FORM_COUNT: self.total_form_count(),
                INITIAL_FORM_COUNT: self.initial_form_count(),
                MIN_NUM_FORM_COUNT: self.min_num,
                MAX_NUM_FORM_COUNT: self.max_num
            })
        return form

    def add_fields(self, form, index):
        """A hook for adding extra fields on to each form instance.
        Overrides Django default Field classes.
        """
        initial_form_count = self.initial_form_count()
        if self.can_order:
            # Only pre-fill the ordering field for initial forms.
            if index is not None and index < initial_form_count:
                form.fields[ORDERING_FIELD_NAME] = IntegerField(
                    label=_('Order'),
                    initial=index + 1,
                    required=False,
                    widget=self.get_ordering_widget(),
                )
            else:
                form.fields[ORDERING_FIELD_NAME] = IntegerField(
                    label=_('Order'),
                    required=False,
                    widget=self.get_ordering_widget(),
                )
        if self.can_delete and (self.can_delete_extra or index < initial_form_count):
            form.fields[DELETION_FIELD_NAME] = BooleanField(label=_('Delete'), required=False)

    def as_dict(self):
        """Return enclosed forms as dictionaries."""
        output = {
            'management_form': self.management_form.as_dict(),
            'forms': []
        }
        for form in self:
            output['forms'].append(form.as_dict())
        return output


def formset_factory(form, formset=BaseFormSet, **kwargs):
    return django.forms.formsets.formset_factory(form, formset=formset, **kwargs)
