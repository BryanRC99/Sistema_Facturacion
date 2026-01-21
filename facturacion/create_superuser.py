import os
from django.contrib.auth import get_user_model

def create_superuser_if_needed():
    if os.getenv("CREATE_SUPERUSER") != "True":
        return

    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

    if not username or not password:
        return

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return

    User.objects.create_superuser(username=username, email=email, password=password)
