from collections import deque

from django.db.models import Manager, QuerySet


# TODO 2023-12-12: This should be a utils.function
#  I guess it could take a list of callbacks, too? Then other functions could
#  be applied to each record as they are traversed.
#  Alternatively, and for cases where depth calculation isn't required, just
#  keep a flat list of references and do the extra work somewhere else
#  The reason why "depth" is specific is because it's part of the memo, and the
#  only part that's directly connected to the traversal
#  Since this mutates the given list and objects, the return could be the flat
#  version.
def calculate_depth(
    data_list: list[dict],
    key: str,
    depth_key: str = 'depth',
) -> list:
    """"""
    queue = deque([(id(x), x, 1) for x in data_list])
    memo = set()
    while queue:
        id_, account, depth = queue.popleft()
        if id_ in memo:
            continue
        memo.add(id_)
        account[depth_key] = depth
        queue.extend((id(x), x, depth + 1) for x in account[key])
    return data_list


def traverse_depth(
    data_list: list[dict],
    key: str,
    depth_key: str = 'depth',
) -> list:
    """Updates dictionaries with depth and returns the flattened list."""
    all_ = []
    queue = deque([(id(x), x, 1) for x in data_list])
    memo = set()
    while queue:
        id_, account, depth = queue.popleft()
        if id_ in memo:
            continue
        memo.add(id_)
        all_.append(account)
        account[depth_key] = depth
        queue.extend((id(x), x, depth + 1) for x in account[key])
    return all_


def hierarchy(foreign_key: str, *values):
    # values / extra values for queryset
    # queryset object; values
    # could I use values_list? or in_bulk()?
    qs: QuerySet
    qs = QuerySet()
    data = []
    data_map = {}
    deferred = deque()
    if qs:
        for record in qs.iterator():
            record['descendents'] = []
    return


class AccountManagerAsset(Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(subtype=self.model.Subtype.ASSET)
        )


class AccountManagerLiability(Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(subtype=self.model.Subtype.LIABILITY)
        )


class AccountManagerEquity(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(subtype=self.model.Subtype.EQUITY)


class AccountManagerIncome(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(subtype=self.model.Subtype.INCOME)


class AccountManagerExpense(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(subtype=self.model.Subtype.EXPENSE)


class AccountAssetManagerFinancial(Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(subtype=self.model.Subtype.FINANCIAL)
        )


class AccountAssetManagerReal(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(subtype=self.model.Subtype.REAL)
