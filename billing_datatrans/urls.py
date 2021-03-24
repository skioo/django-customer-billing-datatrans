from django.urls import path

from .views import InitiateRegisterCreditCardView, InitiateReloadAccountView

urlpatterns = [
    path(r'initiate-reload-account', InitiateReloadAccountView.as_view(),
         name='billing_datatrans_initiate_reload_account'),
    path(r'initiate-register-credit-card', InitiateRegisterCreditCardView.as_view(),
         name='billing_datatrans_initiate_register_credit_card'),
]
