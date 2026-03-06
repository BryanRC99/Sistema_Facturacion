from django.urls import path
from .views import ClienteLoginView
from . import views

urlpatterns = [
    path("login/", ClienteLoginView.as_view(), name="login_cliente"),
    path("portal/", views.portal, name="portal_cliente"),
    path("portal/cambiar-password/", views.cambiar_password, name="cambiar_password_cliente"),

    path("portal/facturas/", views.mis_facturas, name="mis_facturas"),
    path("portal/facturas/<int:factura_id>/", views.factura_detalle_cliente, name="cliente_factura_detalle"),
    path("portal/facturas/<int:factura_id>/imprimir/", views.factura_imprimir_cliente, name="cliente_factura_imprimir"),
    path("portal/facturas/<int:factura_id>/descargar/", views.factura_descargar_cliente, name="cliente_factura_descargar"),
    path("portal/mis-datos/", views.mis_datos, name="mis_datos"),
]