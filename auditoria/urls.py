from django.urls import path
from .views import dashboard

app_name = "auditoria"

urlpatterns = [
    path('', dashboard, name='dashboard'),
]
