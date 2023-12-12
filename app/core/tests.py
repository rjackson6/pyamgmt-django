from django.test import TestCase


class BaseTest(TestCase):
    @classmethod
    def create_account(cls):
        from core.models import Account
        Account.objects.create(
            name='TestAccount'
        )

    def test_sanity(self):
        from core.models import Account
        self.create_account()
        self.assertTrue(Account.objects.first())
