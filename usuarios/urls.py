from django.urls import path
from . import views
from .views import AdminLoginView
app_name = "usuarios"

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="login_admin"),
    path("", views.lista_usuarios, name="lista"),
    path("crear/", views.crear_usuario, name="crear"),
    path("password/cambiar/", views.cambiar_password, name="cambiar_password"),

    # ✅ ESTA ES LA QUE FALTA (o no se guardó)
    path("password/logout/", views.cerrar_sesion_post_password, name="password_logout"),

    path("<int:user_id>/ver/", views.ver_usuario, name="ver"),
    path("<int:user_id>/editar/", views.editar_usuario, name="editar"),
    path("<int:user_id>/eliminar/", views.eliminar_usuario, name="eliminar"),
]
