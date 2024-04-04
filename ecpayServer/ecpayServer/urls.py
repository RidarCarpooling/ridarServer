from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', include("payment.urls")),
    path('payment/', include("payment.urls")),
    path('return', include("receive_result.urls")),
    path('refund', include('refund.urls')),
    path('favicon.ico',RedirectView.as_view(url='static/images/favicon.ico')),
    path('admin/', admin.site.urls)
]
