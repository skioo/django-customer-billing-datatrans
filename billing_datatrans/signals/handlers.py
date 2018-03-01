from datatrans.models import AliasRegistration, Payment
from datatrans.signals import alias_registration_done, payment_by_user_done
from django.dispatch import receiver
from structlog import get_logger

from ..actions import handle_alias_registration_notification, handle_payment_by_user_notification

logger = get_logger()


@receiver(payment_by_user_done)
def payment_by_user_done_signal_handler(sender, instance: Payment, **kwargs) -> None:
    logger.debug('payment-by-user-done-signal-received', instance=instance)
    handle_payment_by_user_notification(instance)


@receiver(alias_registration_done)
def alias_registration_done_signal_handler(sender, instance: AliasRegistration, **kwargs) -> None:
    logger.debug('alias-registration-done-signal-received', instance=instance)
    handle_alias_registration_notification(instance)
