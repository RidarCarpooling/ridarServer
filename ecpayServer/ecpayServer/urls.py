from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', include("payment.urls")),
    path('payment', include("payment.urls")),
    path('return', include("receive_result.urls")),
    path('refund', include('refund.urls')),
    path('favicon.ico',RedirectView.as_view(url='favicon.ico')),
    path('checkVersion', include('appVersion.urls')'),
    path('admin/', admin.site.urls)
]
