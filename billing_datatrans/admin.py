from billing.admin import account_owner_search_fields, link_to_account
from django.contrib import admin

from .models import AccountTransactionClientRef, client_ref_to_id


@admin.register(AccountTransactionClientRef)
class AccountTransactionClientRefAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['client_ref', 'created', link_to_account, 'last_lookup']
    search_fields = account_owner_search_fields

    raw_id_fields = ['account']
    readonly_fields = ['created', 'client_ref', 'last_lookup']

    def get_search_results(self, request, queryset, search_term):
        """ The hashid is not stored in the database, if the user enters
        one in the search bar we decode it to an id and search the database for that.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            id_of_search_term_as_client_ref = client_ref_to_id(search_term)
        except ValueError:
            pass
        else:
            queryset |= self.model.objects.filter(id=id_of_search_term_as_client_ref)
        return queryset, use_distinct
