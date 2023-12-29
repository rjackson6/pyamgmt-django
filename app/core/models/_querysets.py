from django.db.models import Case, F, Q, QuerySet, Sum, Value, When


class AccountQuerySet(QuerySet):
    ...


class TxnQuerySet(QuerySet):
    def with_debits(self) -> QuerySet:
        return self.annotate(
            debits=Sum('line_items__amount', filter=Q(line_items__debit=True))
        )

    def with_credits(self) -> QuerySet:
        return self.annotate(
            credits=Sum('line_items__amount', filter=Q(line_items__debit=False))
        )

    def with_balanced(self) -> QuerySet:
        return self.annotate(
            balanced=Case(
                When(debits=F('credits'), then=Value(True)),
                default=Value(False)
            )
        )
