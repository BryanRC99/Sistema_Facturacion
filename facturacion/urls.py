from django.contrib import admin
from django.urls import path, include
from productos.views import lista_productos
from .views import acceso_no_autorizado
from django.conf import settings
from django.conf.urls.static import static
from twofa.auth_views import login_with_2fa


urlpatterns = [
    path('no-autorizado/', acceso_no_autorizado, name='acceso_no_autorizado'),

    # 🔐 LOGIN PERSONALIZADO CON 2FA (ESTO ES LO NUEVO)
    path('accounts/login/', login_with_2fa, name='login'),

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', lista_productos, name='inicio'),
    path('clientes/', include('clientes.urls')),
    path('productos/', include('productos.urls')),
    path('categorias/', include('categorias.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('reportes/', include('reportes.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('auditoria/', include('auditoria.urls', namespace='auditoria')),
    path('', include('facturacion_app.urls')),
    path("2fa/", include("twofa.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )