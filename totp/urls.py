from django.urls import path
from . import views

app_name = "totp"

urlpatterns = [
    path("setup/", views.totp_setup, name="setup"),
    path("confirm/", views.totp_confirm, name="confirm"),
    path("disable/", views.totp_disable, name="disable"),
]
