import os
from pathlib import Path

import cloudinary
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SECURITY
# =========================
# En Render lo pondrás en Environment Variables
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

# En Render pon DEBUG=False
DEBUG = os.getenv("DEBUG", "False") == "True"

# Render te asigna un dominio *.onrender.com
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
    "facturacion-ygt3.onrender.com",
    ".ngrok-free.dev",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.dev",
    "https://*.onrender.com",
    "https://facturacion-ygt3.onrender.com",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

# Si quieres permitir todo mientras pruebas (no recomendado a largo plazo)
# ALLOWED_HOSTS = ["*"]


LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"


# =========================
# MEDIA (Cloudinary)
# =========================
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

LOGO_URL = os.getenv(
    "LOGO_URL",
    "https://res.cloudinary.com/dmhed5kxh/image/upload/v1769004998/logo_vifmb7.png"
)

TRUST_DEVICE_DAYS = 30


# =========================
# EMAIL (Brevo/Sendinblue)
# =========================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp-relay.sendinblue.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))

EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True") == "True"
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False") == "True"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "Sistema de Facturación <no-reply@example.com>"
)


# =========================
# APPLICATIONS
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "clientes",
    "productos",
    "facturacion_app",
    "facturacion",
    "usuarios",
    "categorias",
    "proveedores",
    "reportes",
    "auditoria.apps.AuditoriaConfig",

    "rest_framework",
    "widget_tweaks",

    "cloudinary",
    "cloudinary_storage",

    "twofa",
    "django_user_agents",
]


# =========================
# CLOUDINARY CONFIG (POR ENV VARS)
# =========================
# OJO: en Render debes crear estas variables:
# CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "django_user_agents.middleware.UserAgentMiddleware",

    "facturacion.middleware.LoginRequiredMiddleware",
    "auditoria.middleware.AuditoriaMiddleware",
]


ROOT_URLCONF = "facturacion.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "facturacion.wsgi.application"


# =========================
# DATABASE (Render: DATABASE_URL)
# =========================
# En Render debes crear la env var:
# DATABASE_URL = postgresql://...
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}


# =========================
# PASSWORD VALIDATION
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =========================
# INTERNATIONALIZATION
# =========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True


# =========================
# STATIC FILES (Whitenoise)
# =========================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_DIRS = [
    BASE_DIR / "static"
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
