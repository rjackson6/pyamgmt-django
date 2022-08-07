import json
import pprint

from django.test import TestCase

from pyamgmt.models import Account


class AccountTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.a = a = Account.objects.create(name='a')
        aa = Account.objects.create(name='aa', parent_account=a)
        aaa = Account.objects.create(name='aaa', parent_account=aa)
        aab = Account.objects.create(name='aab', parent_account=aa)
        aac = Account.objects.create(name='aac', parent_account=aa)
        ab = Account.objects.create(name='ab', parent_account=a)
        aba = Account.objects.create(name='aba', parent_account=ab)
        abc = Account.objects.create(name='abc', parent_account=ab)
        ac = Account.objects.create(name='ac', parent_account=a)
        cls.aca = aca = Account.objects.create(name='aca', parent_account=ac)
        acb = Account.objects.create(name='acb', parent_account=ac)
        acc = Account.objects.create(name='acc', parent_account=ac)
        acca = Account.objects.create(name='acca', parent_account=acc)
        cls.accb = accb = Account.objects.create(name='accb', parent_account=acc)
        cls.aaab = aaab = Account.objects.create(name='aaab', parent_account=aaa)

    def test_get_hierarchy(self):
        root_pk = self.a.pk
        hierarchy = Account.objects.get_hierarchy(root_pk=root_pk)
        pprint.pprint(hierarchy)
        root_pk = self.aca.pk
        hierarchy = Account.objects.get_hierarchy(root_pk=root_pk)
        pprint.pprint(hierarchy)

    def test_get_hierarchy_as_json(self):
        root_pk = self.aaab.pk
        hierarchy = Account.objects.get_hierarchy(root_pk=root_pk)
        j = json.dumps(hierarchy)
        pprint.pprint(j)
