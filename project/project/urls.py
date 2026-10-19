# =============================================================================
# FILE: project/urls.py
# -----------------------------------------------------------------------------
# PURPOSE:  The root URL configuration (referenced by settings.py as
#           ROOT_URLCONF). It is the first place Django looks to match an
#           incoming request path to code.
# ROLE:     Routes '/admin/' to Django's built-in admin site and delegates every
#           other path ('') to this application's own URL patterns.
# DEPENDS:  app/urls.py (included below), which maps those paths to view code.
# =============================================================================
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django's built-in admin interface (login + CRUD screens for all models).
    path('admin/', admin.site.urls),
    # Everything else is handled by the 'app' application's URL patterns.
    path('', include('app.urls'))
]
