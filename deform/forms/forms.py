from typing import Any, Optional

import django.forms
from django.forms.utils import ErrorList
from django.utils.html import conditional_escape
from django.utils.translation import gettext as _


class BaseForm(django.forms.BaseForm):
    """Extends BaseForm methods for JSON-friendly output.
    Based on:
    - BaseForm._html_output(), which is now deprecated
    """
    # TODO: Debug hooks
    # TODO: Django 4.x has changed. get_context() and render() are available.
    def __init__(self,
                 data: Optional[dict] = None,
                 files: Optional[dict] = None,
                 auto_id: str = 'id_%s',
                 prefix: Optional[Any] = None,
                 initial: Optional[dict] = None,
                 error_class=ErrorList,
                 label_suffix: Optional[str] = None,
                 empty_permitted: bool = False,
                 field_order: Optional[list] = None,
                 use_required_attribute: Optional[bool] = None,
                 renderer: Optional[type] = None):
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial,
                         error_class=error_class, label_suffix=label_suffix, empty_permitted=empty_permitted,
                         field_order=field_order, use_required_attribute=use_required_attribute, renderer=renderer)

    def add_prefix(self, field_name):
        # print(f'--BaseForm.add_prefix(self, field_name={field_name})')
        return super().add_prefix(field_name)

    def add_initial_prefix(self, field_name):
        # print(f'--BaseForm.add_initial_prefix(self, field_name={field_name})')
        return super().add_initial_prefix(field_name)

    def full_clean(self):
        # print(f'--BaseForm.full_clean()')
        return super().full_clean()

    def as_dict(self) -> dict:
        """Return the data needed to render a form as a JSON-serializable dictionary.
        "Fields" are considered the set of data to render labels, errors, and widgets.

        output = {
            errors: [],
            fields: [
                {
                    'field': {},
                    'label': {},
                    'help_text': {},
                    'errors': [],
                    'initial_field': {}
                }
            ],
            hidden_fields: []
        }
        """
        # output is actually the whole form output, so each field should have errors and such
        output = {
            'errors': self.non_field_errors().copy(),
            'fields': [],  # "widgets"?
            'hidden_fields': []  # used by FormSets
        }
        for name, field in self.fields.items():
            field_data = {
                'errors': [],
                'field': {},
                'initial_field': {},
                'label': {},
                'help_text': {}
            }
            bf = self[name]
            # TODO: Errors as a list
            bf_errors = self.error_class(bf.errors)  # ErrorList.as_ul()
            field_data['errors'].extend(bf_errors)
            if bf.is_hidden:
                if bf_errors:
                    print(str(bf_errors))
                    output['errors'].extend(
                        [_('(Hidden field %(name)s) %(error)s') % {'name': name, 'error': str(e)}
                         for e in bf_errors])
                output['hidden_fields'].append(bf.as_dict())
            else:
                css_classes = bf.css_classes()
                if css_classes:
                    print(css_classes)
                # if errors_on_separate_row...
                if bf.label:
                    label = conditional_escape(bf.label)  # TODO: needed?
                    label = bf.label_tag_as_dict(label) or {}
                else:
                    label = {}
                field_data['label'] = label
                field_data['help_text'] = field.help_text or ''
                field_data['field'] = bf.as_dict()
                if bf.field.show_hidden_initial:
                    field_data['initial_field'] = (bf.as_dict_hidden(only_initial=True))
                output['fields'].append(field_data)
        return output


class Form(django.forms.Form, BaseForm):
    """Overload of BaseForm/Form.
    Method resolution order with (django.forms.Form, BaseForm):
        Form
        django.forms.forms.Form
        BaseForm
        django.forms.forms.BaseForm
        builtins.object
    """
