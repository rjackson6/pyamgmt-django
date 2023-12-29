from django.db.models import Manager


class AccountAssetManagerFinancial(Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(subtype=self.model.Subtype.FINANCIAL)
        )


class AccountAssetManagerReal(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(subtype=self.model.Subtype.REAL)
