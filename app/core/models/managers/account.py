from collections import deque

from django.db.models import Manager

from .._utils import traverse_depth


class AccountManager(Manager):
    def get_hierarchy_list(
        self,
        *,
        root_pk: int = None,
        flat: bool = False,
    ) -> list:
        # TODO 2023-12-12: A "flat" option would be appropriate for node/edge
        #  format
        qs_values = ['pk', 'name', 'parent_account_id']
        qs_account = self.get_queryset().values(*qs_values)
        if root_pk and not qs_account.filter(pk=root_pk).exists():
            raise ValueError(
                f"{self.model} with pk of {root_pk} does not exist"
            )
        data = []
        data_map = {}  # full structure
        deferred = deque()
        root = None
        account: dict
        for account in qs_account.iterator():
            account['child_accounts'] = []
            pk = account['pk']
            data_map[pk] = account
            parent_account_id = account['parent_account_id']
            if root_pk:
                if root_pk == pk:
                    root = account
                    data.append(root)
            elif parent_account_id is None:
                data.append(account)
            if parent_account_id in data_map:
                data_map[parent_account_id]['child_accounts'].append(account)
            elif parent_account_id is not None:
                deferred.append(account)
        # At this point, every record has been seen once
        while deferred:
            account = deferred.popleft()
            parent_account_id = account['parent_account_id']
            if parent_account_id in data_map:
                data_map[parent_account_id]['child_accounts'].append(account)
        # At this point, the full structure is known.
        # If a root id was given, use that as the reference point
        if root:
            memo = set()
            obj = root
            memo.add(id(obj))
            while obj['parent_account_id']:
                parent_account_cp = data_map[obj['parent_account_id']].copy()
                # De-reference the nested data
                # TODO 2023-12-12: this is mostly for the sake of serialization
                del parent_account_cp['child_accounts']
                obj['parent_account'] = parent_account_cp
                obj = obj['parent_account']
                if id(obj) in memo:
                    break
                memo.add(id(obj))
            del obj
        # Analyze depth/level of nesting
        # This is also where post-processing or aggregation could happen, since
        # every _relevant_ record will be visited.
        # TODO 2023-12-12: I think this is the key.
        #  Originally I used this to calculate depth, but it's an obvious way
        #  to visit every record and do extra work.
        # TODO 2023-12-12: Flattening also needs to remove nesting.
        #  Or use another function that doesn't nest at all.
        flattened = traverse_depth(data, 'child_accounts')
        if flat:
            return flattened
        return data

    def get_hierarchy_flat(self) -> list:
        qs_values = ['pk', 'name', 'parent_account_id']
        qs_account = self.get_queryset().values(*qs_values)
        data = []
        data_map = {}
        deferred = deque()
        account: dict
        for account in qs_account.iterator():
            account['child_account_ids'] = []  # just a list, no nesting
            pk = account['pk']
            data_map[pk] = account
            parent_account_id = account['parent_account_id']
            # optional selective stuff would go here
            data.append(account)
            if parent_account_id in data_map:
                data_map[parent_account_id]['child_account_ids'].append(pk)
            elif parent_account_id is not None:
                deferred.append(account)
        while deferred:
            account = deferred.popleft()
            pk = account['pk']
            parent_account_id = account['parent_account_id']
            if parent_account_id in data_map:
                data_map[parent_account_id]['child_account_ids'].append(pk)
        return data

    def get_hierarchy_raw(self, pk):
        """Tries to use recursive CTE?"""

        params = [pk]
        query = ("""\
            WITH RECURSIVE
                cte(n) AS (
                    VALUES(%s)
                    UNION
                    SELECT id
                    FROM core_account, cte
                    WHERE core_account.parent_account_id=cte.n
                )
            SELECT *
            FROM core_account
            WHERE core_account.id IN cte;
        """)
        return self.raw(query, params)


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
