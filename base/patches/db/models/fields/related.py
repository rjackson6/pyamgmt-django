from django.db.models.fields import Field
from django.db.models.fields.related import (
    ForeignKey as _ForeignKey,
    ForeignObject as _ForeignObject,
    ManyToManyField as _ManyToManyField,
    OneToOneField as _OneToOneField,
    RelatedField as _RelatedField,
    lazy_related_operation,
)

from base.utils import camel_case_to_snake_case


class RelatedField(_RelatedField):
    # noinspection PyAttributeOutsideInit
    # noinspection PyUnresolvedReferences
    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        # Skip the immediate superclass
        super(_RelatedField, self).contribute_to_class(
            cls, name, private_only=private_only, **kwargs)

        self.opts = cls._meta

        if not cls._meta.abstract:
            if self.remote_field.related_name:
                related_name = self.remote_field.related_name
            else:
                related_name = self.opts.default_related_name
            if related_name:
                related_name = related_name % {
                    # "class": cls.__name__.lower(),
                    "class": camel_case_to_snake_case(cls.__name__),
                    "model_name": cls._meta.model_name.lower(),
                    "app_label": cls._meta.app_label.lower(),
                }
                self.remote_field.related_name = related_name

            if self.remote_field.related_query_name:
                related_query_name = self.remote_field.related_query_name % {
                    # "class": cls.__name__.lower(),
                    "class": camel_case_to_snake_case(cls.__name__),
                    "app_label": cls._meta.app_label.lower(),
                }
                self.remote_field.related_query_name = related_query_name

            def resolve_related_class(model, related, field):
                field.remote_field.model = related
                field.do_related_class(related, model)

            lazy_related_operation(
                resolve_related_class, cls, self.remote_field.model, field=self
            )


class ForeignObject(_ForeignObject, RelatedField):
    pass


class ForeignKey(_ForeignKey, ForeignObject):
    pass


class OneToOneField(_OneToOneField, ForeignKey):
    pass


class ManyToManyField(_ManyToManyField, RelatedField):
    pass
