from billing.models import Account
from datatrans.models import AliasRegistration, Payment
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from moneyed import Money
from pytest import raises

from billing_datatrans.actions import PreconditionError, handle_alias_registration_notification, \
    handle_payment_by_user_notification, initiate_payment, initiate_register_credit_card


class PreparePaymentTest(TestCase):
    def setUp(self):
        user = User.objects.create()
        self.account = Account.objects.create(owner=user, currency='CHF')

    def test_it_should_prevent_paying_a_zero_amount(self):
        with raises(PreconditionError, match='Can only pay stricty positive amounts.'):
            initiate_payment(self.account, Money(0, 'CHF'))

    def test_it_should_prepare_payment_when_all_is_right(self):
        params = initiate_payment(self.account, Money(10, 'CHF'))
        assert params
        assert not params.use_alias


class PrepareRegisterCreditCardTest(TestCase):
    def setUp(self):
        user = User.objects.create()
        self.account = Account.objects.create(owner=user, currency='CHF')

    def test_it_should_prepare_register_credit_card(self):
        params = initiate_register_credit_card(self.account)
        assert params
        assert params.use_alias


class HandlePaymentByUserNotificationTest(TestCase):
    def setUp(self):
        user = User.objects.create()
        self.account = Account.objects.create(owner=user, currency='CHF')
        self.payment = Payment(
            success=False,
            transaction_id='170717104749732144',
            merchant_id='2222222222',
            request_type='CAA',
            payment_method='VIS',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='bilrZPJ7V',
            amount=Money(10, 'CHF'),
            credit_card_country='CHE',
            response_code='01',
            response_message='Authorized',
            authorization_code='749762145',
            acquirer_authorization_code='104749')

    def test_it_should_reject_a_payment_with_no_account_attached(self):
        with raises(ObjectDoesNotExist,
                    match='AccountTransactionClientRef matching query does not exist.'):
            handle_payment_by_user_notification(self.payment)

    def test_it_should_store_transaction_on_account_regardless_of_success(self):
        params = initiate_payment(self.account, Money(10, 'CHF'))
        assert params.refno == 'bilrZPJ7V'
        transaction = handle_payment_by_user_notification(self.payment)
        assert transaction.account == self.account
        assert not transaction.success
        assert transaction.invoice is None
        assert transaction.amount == Money(10, 'CHF')
        assert transaction.payment_method == 'VIS'
        assert transaction.credit_card_number == '424242xxxxxx4242'
        assert transaction.psp_object == self.payment


class HandleAliasRegistrationTest(TestCase):
    def setUp(self):
        user = User.objects.create()
        self.account = Account.objects.create(owner=user, currency='CHF')
        self.alias_registration = AliasRegistration(
            success=True,
            transaction_id='170707111922838874',
            merchant_id='1111111111',
            request_type='CAA',
            masked_card_number='424242xxxxxx4242',
            card_alias='70119122433810042',
            expiry_month=12,
            expiry_year=18,
            client_ref='bilrZPJ7V',
            amount=Money(0, 'CHF'),
            payment_method='VIS',
            credit_card_country='CHE',
            authorization_code='953988933',
            acquirer_authorization_code='111953',
            response_code='01',
            response_message='check successful')

    def test_it_should_reject_an_alias_registration_with_no_account_attached(self):
        with raises(ObjectDoesNotExist,
                    match='AccountTransactionClientRef matching query does not exist.'):
            handle_alias_registration_notification(self.alias_registration)

    def test_it_should_add_a_credit_card_to_the_account_on_success(self):
        params = initiate_register_credit_card(self.account)
        assert params.refno == 'bilrZPJ7V'
        credit_card = handle_alias_registration_notification(self.alias_registration)
        assert credit_card
        assert credit_card.account == self.account
        assert credit_card.type == 'VIS'
        assert credit_card.number == '424242xxxxxx4242'
        assert credit_card.expiry_month == 12
        assert credit_card.expiry_year == 18
        assert credit_card.psp_object == self.alias_registration
