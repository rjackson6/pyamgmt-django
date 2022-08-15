from django.db import models


class OneToOneTableBase(models.Model):
    name = models.CharField(max_length=31, unique=True)


class OneToOneTableSubclass(models.Model):
    onetoonetablebase = models.OneToOneField(OneToOneTableBase, on_delete=models.CASCADE, primary_key=True)
    subclass_name = models.CharField(max_length=31)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('onetoonetablebase', 'subclass_name'),
                name='uix_onetoonetablesubclass'
            )
        ]


class OneToOneParentLinkBase(models.Model):
    name = models.CharField(max_length=31, unique=True)


class OneToOneParentLinkSubclass(models.Model):
    # I think I broke this because parent_link doesn't belong on a normal
    #  model.
    onetooneparentlinkbase = models.OneToOneField(
        OneToOneParentLinkBase,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True)
    subclass_name = models.CharField(max_length=31)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('onetooneparentlinkbase', 'subclass_name'),
                name='uix_onetooneparentlinksubclass'
            )
        ]


class MultiTableBase(models.Model):
    name = models.CharField(max_length=31, unique=True)


class MultiTableSubclass(MultiTableBase):
    subclass_name = models.CharField(max_length=31)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('multitablebase_ptr', 'subclass_name'),
                name='uix_multitablesubclass'
            )
        ]


class MultiTableWithPtrBase(models.Model):
    name = models.CharField(max_length=31, unique=True)


class MultiTableWithPtrSubclass(MultiTableWithPtrBase):
    superclass = models.OneToOneField(
        MultiTableWithPtrBase,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True)
    subclass_name = models.CharField(max_length=31)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('superclass', 'subclass_name'),
                name='uix_multitablewithptrsubclass'
            )
        ]
