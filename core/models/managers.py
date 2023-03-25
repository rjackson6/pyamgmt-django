from collections import defaultdict, deque

from django.db.models import Manager


class AccountManager(Manager):
    def get_hierarchy_dd(self, *, root_pk: int = None) -> dict:
        qs_values = ['pk', 'name', 'parent_account_id']
        qs_account = self.get_queryset().values(*qs_values)
        data = {}
        deferred = deque()
        for account in qs_account.iterator():
            account = defaultdict(list, account)
            pk = account['pk']
            data[pk] = account
            parent_account_id = account['parent_account_id']
            if parent_account_id in data:
                data[parent_account_id]['child_accounts'].append(account)

    def get_hierarchy(self, *, root_pk: int = None) -> dict:
        qs_values = ['pk', 'name', 'parent_account_id']
        qs_account = self.get_queryset().values(*qs_values)
        data = {}
        deferred = deque()
        for account in qs_account.iterator():
            pk = account['pk']
            data[pk] = account
            parent_account_id = account['parent_account_id']
            if parent_account_id in data:
                (
                    data[parent_account_id]
                    .setdefault('child_accounts', [])
                    .append(account)
                )
            elif parent_account_id is not None:
                deferred.append(account)
        while deferred:
            account = deferred.popleft()
            parent_account_id = account['parent_account_id']
            if parent_account_id in data:
                (
                    data[parent_account_id]
                    .setdefault('child_accounts', [])
                    .append(account)
                )
        root = data[root_pk]
        obj = root
        while obj.get('parent_account_id', None):
            parent_account_cp = data[obj['parent_account_id']].copy()
            del parent_account_cp['child_accounts']
            obj['parent_account'] = parent_account_cp
            obj = obj['parent_account']
        del obj
        queue = deque([(id(root), root, 1)])
        memo = set()
        while queue:
            id_, account, level = queue.popleft()
            if id_ in memo:
                continue
            memo.add(id_)
            account['level'] = level
            if child_accounts := account.get('child_accounts', []):
                queue += ((id(x), x, level + 1) for x in child_accounts)
        return root


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


class MusicArtistToPersonManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('music_artist', 'person')
