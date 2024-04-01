from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("payment.urls")),
    path('payment/', include("payment.urls")),
    path('return', include("receive_result.urls")),
    path('refund', include('refund.urls')),
    path('admin/', admin.site.urls)
]
