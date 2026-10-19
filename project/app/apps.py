# =============================================================================
# FILE: app/apps.py
# -----------------------------------------------------------------------------
# PURPOSE:  Configuration for this Django application. Django loads one
#           AppConfig class per app; settings.py references it as
#           'app.apps.AppConfig'.
# ROLE:     Tells Django the app's import name ('app') and which default field
#           type to use for automatically-generated primary keys.
# USED BY:  Django at startup (via INSTALLED_APPS in settings.py).
# =============================================================================
from django.apps import AppConfig


class AppConfig(AppConfig):
    # Default type for auto-created 'id' primary keys (64-bit integer).
    default_auto_field = 'django.db.models.BigAutoField'
    # Import name of this application; must match the package folder.
    name = 'app'
