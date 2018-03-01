from billing.models import Account
from django.test import TestCase
from pytest import raises

from billing_datatrans.models import AccountTransactionClientRef


class AccountTransactionClientRefTest(TestCase):
    def test_it_should_allow_finding_by_client_ref(self):
        account = Account.objects.create(owner_id=1234, currency=' CHF')
        cr1 = AccountTransactionClientRef.objects.create(account=account)
        cr2 = AccountTransactionClientRef.objects.create(account=account)
        assert cr1.client_ref == 'bilrZPJ7V'
        assert cr2.client_ref == 'bil97E6Qp'

        assert AccountTransactionClientRef.objects.get_by_client_ref('bilrZPJ7V') == cr1

    def test_it_should_detect_invalid_client_refs(self):
        with raises(ValueError, match="Invalid clientref 'bobabcde': incorrect prefix"):
            AccountTransactionClientRef.objects.get_by_client_ref('bobabcde')

        with raises(ValueError, match="Invalid clientref 'bilabcde': hashid is invalid"):
            AccountTransactionClientRef.objects.get_by_client_ref('bilabcde')

        with raises(ValueError, match="Invalid clientref 'bilZ6rIMZ': hashid decodes to more than one value"):
            AccountTransactionClientRef.objects.get_by_client_ref('bilZ6rIMZ')
