from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_categorias, name='lista_categorias'),
    path('crear/', views.crear_categoria, name='crear_categoria'),
    path('editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path("export/pdf/", views.export_categorias_pdf, name="categorias_export_pdf"),
    path("export/excel/", views.export_categorias_excel, name="categorias_export_excel"),
]
