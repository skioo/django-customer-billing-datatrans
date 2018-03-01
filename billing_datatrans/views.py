from billing.models import Account
from django.shortcuts import get_object_or_404
from djmoney.settings import CURRENCY_CHOICES, DEFAULT_CURRENCY
from moneyed import Money
from rest_framework import permissions, serializers
from rest_framework.decorators import permission_classes
from rest_framework.fields import ChoiceField, DecimalField
from rest_framework.response import Response
from rest_framework.views import APIView

from .actions import initiate_payment, initiate_register_credit_card


class PaymentParametersSerializer(serializers.Serializer):
    merchant_id = serializers.CharField(max_length=20)
    amount = serializers.IntegerField()
    currency = serializers.CharField(max_length=3)
    refno = serializers.CharField(max_length=18)
    sign = serializers.CharField(max_length=40)
    use_alias = serializers.BooleanField()


##################################################


class LoadAccountSerializer(serializers.Serializer):
    """
    First tried to just declare a djmoney.contrib.MoneyField, but currency was still missing from the representation.
    (The currency we can see in the documentation only comes to life when there is a database MoneyField in a model).
    """
    amount = DecimalField(max_digits=12, decimal_places=2)
    amount_currency = ChoiceField(choices=CURRENCY_CHOICES, default=DEFAULT_CURRENCY)


@permission_classes([permissions.IsAuthenticated])
class InitiateReloadAccountView(APIView):
    """
    post: Initiate a reload of the user's account. Returns datatrans params.

    A user has a single billing account, so this endpoint doesn't take an account parameter.
    The account gets inferred from the connected user.
    """

    def get_serializer(self, *args, **kwargs):
        """ Implemet so the automatic documentation generator can find the serializer and its fields. """
        return LoadAccountSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = LoadAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = Money(amount=serializer.validated_data['amount'],
                       currency=serializer.validated_data['amount_currency'])
        account = get_object_or_404(Account, owner=request.user)
        payment_parameters = initiate_payment(account=account, amount=amount)
        return Response(PaymentParametersSerializer(payment_parameters).data)


##################################################

@permission_classes([permissions.IsAuthenticated])
class InitiateRegisterCreditCardView(APIView):
    """
    post: Initiate the credit card registration on the user's account. Returns datatrans params.

    A user has a single billing account, so this endpoint doesn't take an account parameter.
    The account gets inferred from the connected user.
    """

    def post(self, request, *args, **kwargs):
        account = get_object_or_404(Account, owner=request.user)
        payment_parameters = initiate_register_credit_card(account=account)
        return Response(PaymentParametersSerializer(payment_parameters).data)
