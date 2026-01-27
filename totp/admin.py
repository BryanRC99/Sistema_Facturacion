from django.contrib import admin
from .models import TOTPProfile


@admin.register(TOTPProfile)
class TOTPProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "enabled", "updated_at")
    list_filter = ("enabled",)
    search_fields = ("user__username", "user__email")
