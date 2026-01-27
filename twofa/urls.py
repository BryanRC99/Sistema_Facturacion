from django.urls import path
from .views import verify_2fa, forget_device
from . import views

app_name = "twofa"

urlpatterns = [
    path("verificar/", verify_2fa, name="verify"),
    path("olvidar-dispositivo/", forget_device, name="forget_device"),
]
