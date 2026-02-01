from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proveedores, name='lista_proveedores'),
    path('crear/', views.crear_proveedor, name='crear_proveedor'),
    path('editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path("export/pdf/", views.export_proveedores_pdf, name="proveedores_export_pdf"),
    path("export/excel/", views.export_proveedores_excel, name="proveedores_export_excel"),
]
