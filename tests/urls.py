from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path(r'billing/', include('billing.urls')),
    path(r'admin/', admin.site.urls),
]
