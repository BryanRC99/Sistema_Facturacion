from django.urls import path
from . import views


urlpatterns = [
    # Facturas
    path('facturas/', views.lista_facturas, name='factura_lista'),
    path('facturas/nueva/', views.crear_factura, name='factura_crear'),
    path('facturas/<int:id>/', views.ver_factura, name='factura_detalle'),
    path('facturas/<int:id>/anular/', views.anular_factura, name='factura_anular'),
    path('facturas/<int:id>/imprimir/', views.imprimir_factura, name='imprimir_factura'),
    path("export/pdf/", views.export_facturas_pdf, name="facturas_export_pdf"),
    path("export/excel/", views.export_facturas_excel, name="facturas_export_excel"),

    # AJAX
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
    path('cliente_info/<int:id>/', views.cliente_info, name='cliente_info'),
]
