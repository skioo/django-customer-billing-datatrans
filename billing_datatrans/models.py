"""
An AccountTransactionClientRef associates a billing account with a datatrans clientref.
A client-ref is a string that is sent to datatrans when a user is about to perform a payment or a credit-card
registration, once the user is done datatrans calls our webhook with the client-ref.
The client-ref is the only thing linking a user's intent with transactions that occur within datatrans, so we've spent
some effort making sure that client-refs are unique:
- Each use-case uses a different prefix when talking to datatrans. This billing_datatrans bridge uses the `bil` prefix.
- Each environment (dev, staging, production, etc) uses a different hashid salt, which makes collisions unlikely.


Implementation:
The hashid is not stored because it is based on the id, the id is generated in the database,
so storing the hashid would require two database transactions. The main downside of this design
is that it is not possible to directly search for a hashid in the database.

"""
from numbers import Number

from billing.models import Account
from django.conf import settings
from django.db import models
from django.db.models import PROTECT
from django.utils import timezone
from hashids import Hashids

CLIENT_REF_PREFIX = 'bil'  # Marks this clientref as belonging to the billing system.

hashids = Hashids(salt=settings.BILLING_DATATRANS_HASHID_SALT, min_length=6)


def client_ref_to_id(client_ref: str) -> Number:
    if not client_ref.startswith(CLIENT_REF_PREFIX):
        raise ValueError("Invalid clientref '{}': incorrect prefix".format(client_ref))
    h = client_ref[3:]
    decoded = hashids.decode(h)  # decode always returns a tuple, with variable-length
    if len(decoded) == 0:
        raise ValueError("Invalid clientref '{}': hashid is invalid".format(client_ref))
    elif len(decoded) > 1:
        raise ValueError("Invalid clientref '{}': hashid decodes to more than one value".format(client_ref))
    else:
        return decoded[0]


def id_to_client_ref(id: Number) -> str:
    return '{}{}'.format(CLIENT_REF_PREFIX, hashids.encode(id))


class AccountTransactionClientRefManager(models.Manager):
    def get_by_client_ref(self, client_ref: str):
        # Note: The value of last_lookup will be fine even if multiple threads call this concurrently.
        atcr = self.get(id=client_ref_to_id(client_ref))
        atcr.last_lookup = timezone.now()
        atcr.save()
        return atcr


class AccountTransactionClientRef(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    account = models.ForeignKey(Account, on_delete=PROTECT)
    last_lookup = models.DateTimeField(null=True, blank=True)

    objects = AccountTransactionClientRefManager()

    @property
    def client_ref(self):
        if self.id:
            return id_to_client_ref(self.id)

    def __str__(self):
        return 'Account Transaction Client Ref {}'.format(self.client_ref)
