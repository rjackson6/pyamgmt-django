import copy
from functools import partialmethod
from itertools import chain

from django.apps import apps
from django.conf import settings
from django.core.exceptions import (
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)
from django.db.models.base import (
    _has_contribute_to_class,  # noqa
    Model as _Model,
    ModelBase as _ModelBase,
    make_foreign_order_accessors,
    subclass_exception,
)
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import (
    OneToOneField,
    lazy_related_operation,
    resolve_relation,
)
from django.db.models.manager import Manager
from django.db.models.signals import class_prepared
# from django.db.models.utils import make_model_tuple

from base.db.models.options import Options
from base.db.models.utils import make_model_tuple


# noinspection PyProtectedMember
# noinspection PyUnresolvedReferences
# noinspection SpellCheckingInspection
class ModelBase(_ModelBase):
    def __new__(mcs, name, bases, attrs, **kwargs):
        super_new = super(_ModelBase, mcs).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(mcs, name, bases, attrs)

        # Create the class.
        module = attrs.pop("__module__")
        new_attrs = {"__module__": module}
        classcell = attrs.pop("__classcell__", None)
        if classcell is not None:
            new_attrs["__classcell__"] = classcell
        attr_meta = attrs.pop("Meta", None)
        # Pass all attrs without a (Django-specific) contribute_to_class()
        # method to type.__new__() so that they're properly initialized
        # (i.e. __set_name__()).
        contributable_attrs = {}
        for obj_name, obj in attrs.items():
            if _has_contribute_to_class(obj):
                contributable_attrs[obj_name] = obj
            else:
                new_attrs[obj_name] = obj
        new_class = super_new(mcs, name, bases, new_attrs, **kwargs)

        abstract = getattr(attr_meta, "abstract", False)
        meta = attr_meta or getattr(new_class, "Meta", None)
        base_meta = getattr(new_class, "_meta", None)

        app_label = None

        # Look for an application configuration to attach the model to.
        app_config = apps.get_containing_app_config(module)

        if getattr(meta, "app_label", None) is None:
            if app_config is None:
                if not abstract:
                    raise RuntimeError(
                        "Model class %s.%s doesn't declare an explicit "
                        "app_label and isn't in an application in "
                        "INSTALLED_APPS." % (module, name)
                    )

            else:
                app_label = app_config.label

        new_class.add_to_class("_meta", Options(meta, app_label))
        if not abstract:
            new_class.add_to_class(
                "DoesNotExist",
                subclass_exception(
                    "DoesNotExist",
                    tuple(
                        x.DoesNotExist
                        for x in parents
                        if hasattr(x, "_meta") and not x._meta.abstract
                    )
                    or (ObjectDoesNotExist,),
                    module,
                    attached_to=new_class,
                ),
            )
            new_class.add_to_class(
                "MultipleObjectsReturned",
                subclass_exception(
                    "MultipleObjectsReturned",
                    tuple(
                        x.MultipleObjectsReturned
                        for x in parents
                        if hasattr(x, "_meta") and not x._meta.abstract
                    )
                    or (MultipleObjectsReturned,),
                    module,
                    attached_to=new_class,
                ),
            )
            if base_meta and not base_meta.abstract:
                # Non-abstract child classes inherit some attributes from their
                # non-abstract parent (unless an ABC comes before it in the
                # method resolution order).
                if not hasattr(meta, "ordering"):
                    new_class._meta.ordering = base_meta.ordering
                if not hasattr(meta, "get_latest_by"):
                    new_class._meta.get_latest_by = base_meta.get_latest_by

        is_proxy = new_class._meta.proxy

        # If the model is a proxy, ensure that the base class
        # hasn't been swapped out.
        if is_proxy and base_meta and base_meta.swapped:
            raise TypeError(
                "%s cannot proxy the swapped model '%s'." % (name, base_meta.swapped)
            )

        # Add remaining attributes (those with a contribute_to_class() method)
        # to the class.
        for obj_name, obj in contributable_attrs.items():
            new_class.add_to_class(obj_name, obj)

        # All the fields of any type declared on this model
        new_fields = chain(
            new_class._meta.local_fields,
            new_class._meta.local_many_to_many,
            new_class._meta.private_fields,
        )
        field_names = {f.name for f in new_fields}

        # Basic setup for proxy models.
        if is_proxy:
            base = None
            for parent in [kls for kls in parents if hasattr(kls, "_meta")]:
                if parent._meta.abstract:
                    if parent._meta.fields:
                        raise TypeError(
                            "Abstract base class containing model fields not "
                            "permitted for proxy model '%s'." % name
                        )
                    else:
                        continue
                if base is None:
                    base = parent
                elif parent._meta.concrete_model is not base._meta.concrete_model:
                    raise TypeError(
                        "Proxy model '%s' has more than one non-abstract model base "
                        "class." % name
                    )
            if base is None:
                raise TypeError(
                    "Proxy model '%s' has no non-abstract model base class." % name
                )
            new_class._meta.setup_proxy(base)
            new_class._meta.concrete_model = base._meta.concrete_model
        else:
            new_class._meta.concrete_model = new_class

        # Collect the parent links for multi-table inheritance.
        parent_links = {}
        for base in reversed([new_class] + parents):
            # Conceptually equivalent to `if base is Model`.
            if not hasattr(base, "_meta"):
                continue
            # Skip concrete parent classes.
            if base != new_class and not base._meta.abstract:
                continue
            # Locate OneToOneField instances.
            for field in base._meta.local_fields:
                if isinstance(field, OneToOneField) and field.remote_field.parent_link:
                    related = resolve_relation(new_class, field.remote_field.model)
                    parent_links[make_model_tuple(related)] = field

        # Track fields inherited from base models.
        inherited_attributes = set()
        # Do the appropriate setup for any model parents.
        for base in new_class.mro():
            if base not in parents or not hasattr(base, "_meta"):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                inherited_attributes.update(base.__dict__)
                continue

            parent_fields = base._meta.local_fields + base._meta.local_many_to_many
            if not base._meta.abstract:
                # Check for clashes between locally declared fields and those
                # on the base classes.
                for field in parent_fields:
                    if field.name in field_names:
                        raise FieldError(
                            "Local field %r in class %r clashes with field of "
                            "the same name from base class %r."
                            % (
                                field.name,
                                name,
                                base.__name__,
                            )
                        )
                    else:
                        inherited_attributes.add(field.name)

                # Concrete classes...
                base = base._meta.concrete_model
                base_key = make_model_tuple(base)
                if base_key in parent_links:
                    field = parent_links[base_key]
                elif not is_proxy:
                    attr_name = "%s_ptr" % base._meta.model_name
                    field = OneToOneField(
                        base,
                        on_delete=CASCADE,
                        name=attr_name,
                        auto_created=True,
                        parent_link=True,
                    )

                    if attr_name in field_names:
                        raise FieldError(
                            "Auto-generated field '%s' in class %r for "
                            "parent_link to base class %r clashes with "
                            "declared field of the same name."
                            % (
                                attr_name,
                                name,
                                base.__name__,
                            )
                        )

                    # Only add the ptr field if it's not already present;
                    # e.g. migrations will already have it specified
                    if not hasattr(new_class, attr_name):
                        new_class.add_to_class(attr_name, field)
                else:
                    field = None
                new_class._meta.parents[base] = field
            else:
                base_parents = base._meta.parents.copy()

                # Add fields from abstract base class if it wasn't overridden.
                for field in parent_fields:
                    if (
                            field.name not in field_names
                            and field.name not in new_class.__dict__
                            and field.name not in inherited_attributes
                    ):
                        new_field = copy.deepcopy(field)
                        new_class.add_to_class(field.name, new_field)
                        # Replace parent links defined on this base by the new
                        # field. It will be appropriately resolved if required.
                        if field.one_to_one:
                            for parent, parent_link in base_parents.items():
                                if field == parent_link:
                                    base_parents[parent] = new_field

                # Pass any non-abstract parent classes onto child.
                new_class._meta.parents.update(base_parents)

            # Inherit private fields (like GenericForeignKey) from the parent
            # class
            for field in base._meta.private_fields:
                if field.name in field_names:
                    if not base._meta.abstract:
                        raise FieldError(
                            "Local field %r in class %r clashes with field of "
                            "the same name from base class %r."
                            % (
                                field.name,
                                name,
                                base.__name__,
                            )
                        )
                else:
                    field = copy.deepcopy(field)
                    if not base._meta.abstract:
                        field.mti_inherited = True
                    new_class.add_to_class(field.name, field)

        # Copy indexes so that index names are unique when models extend an
        # abstract model.
        new_class._meta.indexes = [
            copy.deepcopy(idx) for idx in new_class._meta.indexes
        ]

        if abstract:
            # Abstract base models can't be instantiated and don't appear in
            # the list of models for an app. We do the final setup for them a
            # little differently from normal models.
            attr_meta.abstract = False
            new_class.Meta = attr_meta
            return new_class

        new_class._prepare()
        new_class._meta.apps.register_model(new_class._meta.app_label, new_class)
        return new_class

    def _prepare(cls):
        """Create some methods once self._meta has been populated."""
        opts = cls._meta
        opts._prepare(cls)

        if opts.order_with_respect_to:
            cls.get_next_in_order = partialmethod(
                cls._get_next_or_previous_in_order, is_next=True
            )
            cls.get_previous_in_order = partialmethod(
                cls._get_next_or_previous_in_order, is_next=False
            )

            # Defer creating accessors on the foreign class until it has been
            # created and registered. If remote_field is None, we're ordering
            # with respect to a GenericForeignKey and don't know what the
            # foreign class is - we'll add those accessors later in
            # contribute_to_class().
            if opts.order_with_respect_to.remote_field:
                wrt = opts.order_with_respect_to
                remote = wrt.remote_field.model
                lazy_related_operation(make_foreign_order_accessors, cls, remote)

        # Give the class a docstring -- its definition.
        if cls.__doc__ is None:
            cls.__doc__ = "%s(%s)" % (
                cls.__name__,
                ", ".join(f.name for f in opts.fields),
            )

        get_absolute_url_override = settings.ABSOLUTE_URL_OVERRIDES.get(
            opts.label_lower
        )
        if get_absolute_url_override:
            setattr(cls, "get_absolute_url", get_absolute_url_override)

        if not opts.managers:
            if any(f.name == "objects" for f in opts.fields):
                raise ValueError(
                    "Model %s must specify a custom Manager, because it has a "
                    "field named 'objects'." % cls.__name__
                )
            manager = Manager()
            manager.auto_created = True
            cls.add_to_class("objects", manager)

        # Set the name of _meta.indexes. This can't be done in
        # Options.contribute_to_class() because fields haven't been added to
        # the model at that point.
        for index in cls._meta.indexes:
            if not index.name:
                index.set_name_with_model(cls)

        class_prepared.send(sender=cls)


class Model(_Model, metaclass=ModelBase):
    pass
