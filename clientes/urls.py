from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('crear/', views.crear_cliente, name='crear_cliente'),
    path('editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path("export/pdf/", views.export_clientes_pdf, name="clientes_export_pdf"),
    path("export/excel/", views.export_clientes_excel, name="clientes_export_excel"),
]
