from billing.psp import PSP
from datatrans import gateway
from datatrans.models import AliasRegistration, Payment
from django.db.models import Model
from moneyed import Money
from typing import Tuple


class DatatransPSP(PSP):
    def model_classes(self):
        return [AliasRegistration, Payment]

    def charge_credit_card(self, credit_card_psp_object: Model, amount: Money, client_ref: str) -> Tuple[bool, Model]:
        payment = gateway.pay_with_alias(amount=amount,
                                         alias_registration_id=credit_card_psp_object.pk,
                                         client_ref=client_ref)
        return payment.success, payment

    def refund_payment(self, payment_psp_object: Model, amount: Money, client_ref: str) -> Tuple[bool, Model]:
        refund = gateway.refund(value=amount,
                                payment_transaction_id=payment_psp_object.pk,
                                client_ref=client_ref)
        return refund.success, refund
