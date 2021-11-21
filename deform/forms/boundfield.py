__all__ = ['BoundField']

from typing import Optional, Union

import django.forms.boundfield
import django.forms.widgets
from django.utils.html import conditional_escape, format_html
from django.utils.translation import gettext_lazy as _


class BoundField(django.forms.boundfield.BoundField):
    """Provides additional methods.
    Based on:
    - as_widget()

    """
    def as_dict_output(self) -> dict:
        """Clone of __str__() method"""
        # TODO: this is the only case where a BoundField will return two "fields"
        #  The name of the hidden default will be different, if I could key it
        #  Alternatively, somehow appending it as its own dictionary would be ideal
        #  They group side-by-side just because of HTML rendering in the original method
        #  Note: The field has nothing to do with errors, labels, or help_text.
        if self.field.show_hidden_initial:
            return self.as_dict_hidden(only_initial=True)
        return self.as_dict()

    def as_dict(self,
                widget: django.forms.widgets.Widget = None,
                attrs: Optional[dict] = None,
                only_initial: bool = False) -> dict:
        """Clone of as_widget() method, bypassing widget.render().
        Returns a dictionary with the data for one self-contained widget.
        """
        widget = widget or self.field.widget
        if self.field.localize:
            widget.is_localized = True
        attrs = attrs or {}
        attrs = self.build_widget_attrs(attrs, widget)
        if self.auto_id and 'id' not in widget.attrs:
            attrs.setdefault('id', self.html_initial_id if only_initial else self.auto_id)
        # Normally this calls widget.render(); bypass and go to get_context()
        # Note: duplicate query around here for choice fields from getting the first choice. Happens natively, too.
        widget_context = widget.get_context(
            name=self.html_initial_name if only_initial else self.html_name,
            value=self.value(),
            attrs=attrs
        )
        # subwidget handling for things like ModelChoiceIteratorValue
        # Normally these are formatted out to string in the widget template
        for optgroup in widget_context['widget'].get('optgroups', []):
            for option in optgroup[1]:
                value = option.get('value')  # TODO: default '' ?
                if value is not None and not isinstance(value, str):
                    option['value'] = str(value)
        return widget_context['widget']

    def as_dict_hidden(self,
                       attrs: Optional[dict] = None,
                       **kwargs) -> dict:
        return self.as_dict(self.field.hidden_widget(), attrs, **kwargs)

    def label_tag_as_dict(self,
                          contents: Optional[str] = None,
                          attrs: Optional[dict] = None,
                          label_suffix=None) -> dict:
        """Similar to label_tag(), but without rendering.
        output = {
            'attrs': {},
            'text': ''
        }
        """
        contents = contents or self.label  # str, "text"
        if label_suffix is None:
            label_suffix = (self.field.label_suffix if self.field.label_suffix is not None
                            else self.form.label_suffix)
        if label_suffix and contents and contents[-1] not in _(':?.!'):
            contents = format_html('{}{}', contents, label_suffix)
        widget = self.field.widget
        id_ = widget.attrs.get('id') or self.auto_id
        if id_:
            id_for_label = widget.id_for_label(id_)  #
            if id_for_label:
                attrs = {**(attrs or {}), 'for': id_for_label}  #
                print(attrs)
            if self.field.required and hasattr(self.form, 'required_css_class'):
                attrs = attrs or {}
                if 'class' in attrs:
                    # TODO: may not need this as the string 'class="some css class"'
                    attrs['class'] += ' ' + self.form.required_css_class
                else:
                    # TODO: as with above, could use a list of classes instead
                    attrs['class'] = self.form.required_css_class
                # attrs = flatatt(attrs) if attrs else ''  # keep dictionary
                # contents = format_html() not needed
        else:
            contents = conditional_escape(contents)
        # return mark_safe(contents)
        output = {
            'attrs': attrs or {},
            'text': contents
        }
        return output

    def css_classes_as_list(self,
                            extra_classes: Optional[Union[list, str]] = None) -> list:
        """Similar to css_classes(), returning a list instead of a space-separated string.
        Might be able to return as a set, too, but a list is guaranteed to be JSON-friendly.
        """
        if hasattr(extra_classes, 'split'):  # split into if it's a string
            extra_classes = extra_classes.split()
        extra_classes = set(extra_classes or [])
        if self.errors and hasattr(self.form.error_css_class, 'error_css_class'):
            extra_classes.add(self.form.error_css_class)
        if self.field.required and hasattr(self.form, 'required_css_class'):
            extra_classes.add(self.form.required_css_class)
        return list(extra_classes)
