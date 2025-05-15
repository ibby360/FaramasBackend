from django.contrib import admin
from faramas.profiles.models import UserProfile

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin view for UserProfile model.
    """
    list_display = (
        "user",
        "bio",
        "location",
        "verifica_status",
        "is_broker",
        "is_verified",
    )
    search_fields = ("user__email",)
    list_filter = ("verifica_status", "is_broker", "is_verified")
    ordering = ("-user__date_joined",)
