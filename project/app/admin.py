# =============================================================================
# FILE: app/admin.py
# -----------------------------------------------------------------------------
# PURPOSE:  Registers the app's models with Django's built-in admin site so they
#           can be created/edited/deleted through the /admin/ web interface.
# ROLE:     This is how staff (especially brokers) manage content that has no
#           dedicated page in the app, such as Reviews and Partners, and how a new
#           user's role is set (e.g. promoted to 'broker').
# USED BY:  Django admin, reachable at /admin/ (wired up in project/urls.py).
# =============================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CommissionSlip,
    CustomUser,
    FavoriteProperty,
    Partner,
    Property,
    PropertyImage,
    PropertyInquiry,
    Review,
    Seminar,
    SeminarRegistration,
)

class CustomUserAdmin(UserAdmin):
    """Customizes the admin screen for user accounts.

    Adds the role (user_type) and verification columns and lets staff filter by
    them; this is also how a new account is promoted to 'broker' (see README).
    """
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_verified', 'is_staff']   # Columns in the user list.
    list_filter = ['user_type', 'is_verified', 'is_staff', 'is_superuser']        # Sidebar filters.
    # Publicly registered accounts start as buyers. Staff can promote them by
    # editing their role and verification status here.
    fieldsets = UserAdmin.fieldsets + (
        ('Role and profile', {'fields': ('user_type', 'phone', 'is_verified')}),
    )

# Register the custom user model with its tailored admin class.
admin.site.register(CustomUser, CustomUserAdmin)
# Register the remaining models with Django's default admin screens.
admin.site.register(Property)
admin.site.register(PropertyImage)
admin.site.register(Review)
admin.site.register(FavoriteProperty)
admin.site.register(PropertyInquiry)
admin.site.register(Seminar)
admin.site.register(SeminarRegistration)
admin.site.register(CommissionSlip)

# The @admin.register decorator registers a model while also defining a custom
# admin class for it in one place (an alternative to admin.site.register above).
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    """Admin screen for Partner logos: shows the name and website columns."""
    list_display = ('name', 'website')
