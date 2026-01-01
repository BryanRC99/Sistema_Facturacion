from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.lista_usuarios, name="lista"),
    path("crear/", views.crear_usuario, name="crear"),
    path("<int:user_id>/ver/", views.ver_usuario, name="ver"),
    path("<int:user_id>/editar/", views.editar_usuario, name="editar"),
    path("<int:user_id>/eliminar/", views.eliminar_usuario, name="eliminar"),
]
