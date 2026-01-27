from django.urls import path
from reportes import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('ventas/rango/', views.reporte_ventas_rango, name='reporte_ventas_rango'),
    path('ventas/metodos-pago/', views.reporte_metodos_pago, name='reporte_metodos_pago'),
    path('ventas/clientes/', views.reporte_clientes, name='reporte_clientes'),
    path('ventas/productos/', views.reporte_productos, name='reporte_productos'),
    path('ventas/categorias/', views.reporte_categorias, name='reporte_categorias'),
    path('ventas/anuladas/', views.reporte_anuladas, name='reporte_anuladas'),
    path('ventas/vendedores/', views.reporte_vendedores, name='reporte_vendedores'),
    path('ventas/utilidad/', views.reporte_utilidad, name='reporte_utilidad'),
]
