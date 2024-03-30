from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('return', include("receive_result.urls")),
    path('', include("payment.urls")),
    path('payment/', include("payment.urls")),
    path('admin/', admin.site.urls)
]
