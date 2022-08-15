import logging

from django.test import TestCase

from pyamgmt.models import *
from pyamgmt.forms import *

logger = logging.getLogger(__name__)


# The thing I think I was thinking about was cleaned_data and instance
#  I don't think they are the same. I need to double-check how that data is
#  retrieved.


class AccountFormTests(TestCase):
    def test_create(self):
        form_data = {
            'name': 'Account001'
        }
        form = AccountForm(data=form_data)
        if form.is_valid():
            obj = form.save()
            self.assertIs(obj, form.instance)

    def test_create_non_commit(self):
        form_data = {
            'name': 'Account001'
        }
        form = AccountForm(data=form_data)
        if form.is_valid():
            obj = form.save(commit=False)
            self.assertIs(obj, form.instance)

    def test_update(self):
        account = Account.objects.create(name='account001')
        form = AccountForm(data={'subtype': 'ASSET'}, instance=account)
        if form.is_valid():
            obj = form.save()
            self.assertIs(obj, form.instance)


class AccountAssetFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        account = Account.objects.create(name='Account555', subtype='ASSET')
        accountasset = AccountAsset.objects.create(subtype='REAL', account=account)
