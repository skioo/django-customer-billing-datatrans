from billing.models import Account, CreditCard, Invoice, Transaction
from billing.signals import credit_card_registered
from datatrans.gateway import (
    PaymentParameters,
    build_payment_parameters,
    build_register_credit_card_parameters,
)
from datatrans.models import AliasRegistration, Payment, Refund
from moneyed import Money
from structlog import get_logger
from typing import Optional

from .models import AccountTransactionClientRef, CLIENT_REF_PREFIX

logger = get_logger()


class PreconditionError(Exception):
    pass


def initiate_payment(account: Account, amount: Money) -> PaymentParameters:
    logger.debug('initiate-payment', account=account, amount=amount)
    if amount.amount <= 0:
        raise PreconditionError('Can only pay stricty positive amounts.')
    transaction_client_ref = AccountTransactionClientRef.objects.create(account=account)
    return build_payment_parameters(amount=amount, client_ref=transaction_client_ref.client_ref)


def initiate_register_credit_card(account: Account) -> PaymentParameters:
    logger.debug('initiate-credit-card-registration', account=account)
    transaction_client_ref = AccountTransactionClientRef.objects.create(account=account)
    return build_register_credit_card_parameters(client_ref=transaction_client_ref.client_ref)


def handle_payment_by_user_notification(payment: Payment) -> Transaction:
    """
    Adds a transaction to the related account (regardless of the transaction success)

    :param payment: A payment notified by datatatrans (either successful or not)
    :return: The transaction
    """
    logger.debug('handling-payment-by-user-notification', payment=payment)
    transaction_client_ref = AccountTransactionClientRef.objects.get_by_client_ref(payment.client_ref)

    transaction = Transaction.objects.create(
        account=transaction_client_ref.account,
        success=payment.success,
        amount=payment.amount,
        payment_method=payment.payment_method,
        credit_card_number=payment.masked_card_number,
        psp_object=payment)
    logger.debug('transaction-created', transaction_id=transaction.pk)
    return transaction


def handle_alias_registration_notification(alias_registration: AliasRegistration) -> Optional[CreditCard]:
    """
    If the alias registration was a success, adds a CreditCard to the related account.

    :param alias_registration: An alias registration notification (either successful or not)
    :return: The registered credit card, or None if registration was unsuccessful.
    """
    logger.debug('handling-alias-registration-notification', alias_registration=alias_registration)
    transaction_client_ref = AccountTransactionClientRef.objects.get_by_client_ref(alias_registration.client_ref)

    if alias_registration.success:
        credit_card = CreditCard.objects.create(
            account=transaction_client_ref.account,
            type=alias_registration.payment_method,
            number=alias_registration.masked_card_number,
            expiry_month=alias_registration.expiry_month,
            expiry_year=alias_registration.expiry_year,
            psp_object=alias_registration)
        logger.debug('credit-card-registered', credit_card_id=credit_card.pk)
        credit_card_registered.send(
            sender=handle_alias_registration_notification,
            credit_card=credit_card
        )
        return credit_card
    else:
        return None


def handle_refund_notification(refund: Refund) -> Transaction:
    """
    Adds a transaction to the related account (regardless of the transaction success)

    :param refund: A refund notified by datatatrans (either successful or not)
    :return: The transaction
    """
    logger.debug('handling-refund-notification', refund=refund)
    invoice_id_or_not = refund.client_ref.split('-')[0]
    if CLIENT_REF_PREFIX in invoice_id_or_not:
        atcr = AccountTransactionClientRef.objects.get_by_client_ref(invoice_id_or_not)
        invoice = None
        account = atcr.account
    else:
        invoice = Invoice.objects.get(id=invoice_id_or_not)
        account = invoice.account

    transaction = Transaction.objects.create(
        invoice=invoice,
        account=account,
        success=refund.success,
        amount=-refund.amount,
        payment_method='RFD',
        credit_card_number='',
        psp_object=refund
    )
    logger.debug('transaction-created', transaction_id=transaction.pk)
    return transaction
