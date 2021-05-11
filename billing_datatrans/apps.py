from billing import psp
from django.apps import AppConfig


class BillingDatatransConfig(AppConfig):
    name = 'billing_datatrans'
    verbose_name = 'Billing Datatrans'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        # DatatransPSP pulls in datatrans model classes, so we have to wait before we import it.
        from .datatrans_psp import DatatransPSP
        psp.register(DatatransPSP())
        # noinspection PyUnresolvedReferences
        from .signals.handlers import payment_by_user_done_signal_handler  # noqa
        # noinspection PyUnresolvedReferences
        from .signals.handlers import alias_registration_done_signal_handler  # noqa
