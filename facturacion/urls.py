from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from productos.views import lista_productos
from .views import acceso_no_autorizado
from twofa.auth_views import login_with_2fa
from usuarios.views import admin_guard

urlpatterns = [

    # =========================
    # SISTEMA
    # =========================
    path('no-autorizado/', acceso_no_autorizado, name='acceso_no_autorizado'),
    path('accounts/login/', login_with_2fa, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),

    # =========================
    # ADMIN PERSONALIZADO
    # =========================
    path("admin/", admin_guard),
    path("django-admin/", admin.site.urls),
    
    # =========================
    # PORTAL CLIENTES
    # =========================
    path("portal-clientes/", include("clientes.urls_portal")),

    # =========================
    # MÓDULOS INTERNOS
    # =========================
    path('clientes/', include('clientes.urls_admin')),
    path('productos/', include('productos.urls')),
    path('categorias/', include('categorias.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('facturas/', include('facturacion_app.urls')),
    path('reportes/', include('reportes.urls')),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('auditoria/', include('auditoria.urls', namespace='auditoria')),
    path("2fa/", include("twofa.urls")),
    path("totp/", include("totp.urls")),

    # =========================
    # FACTURACIÓN (CON PREFIJO)
    # =========================

    # =========================
    # INICIO GENERAL
    # =========================
    path('', lista_productos, name='inicio'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)