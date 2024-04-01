from django.urls import path
from . import views

urlpatterns = [
    path("", views.receive_payment_info, name="index"),
]