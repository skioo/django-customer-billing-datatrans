from django.conf.urls import url

from .views import InitiateRegisterCreditCardView, InitiateReloadAccountView

urlpatterns = [
    url(r'^initiate-reload-account$', InitiateReloadAccountView.as_view(),
        name='billing_datatrans_initiate_reload_account'),
    url(r'^initiate-register-credit-card$', InitiateRegisterCreditCardView.as_view(),
        name='billing_datatrans_initiate_register_credit_card'),
]
