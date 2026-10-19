# =============================================================================
# FILE: project/wsgi.py
# -----------------------------------------------------------------------------
# PURPOSE:  WSGI (Web Server Gateway Interface) entry point. It exposes the
#           module-level 'application' callable that a WSGI web server
#           (Gunicorn, uWSGI, Apache/mod_wsgi, ...) uses to serve this project
#           in production.
# ROLE:     Referenced by settings.py as
#           WSGI_APPLICATION = 'project.wsgi.application'.
# NOTE:     Django's development server (manage.py runserver) uses it as well.
# =============================================================================
"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Tell Django which settings module to use, then build the WSGI 'application'
# callable that the web server invokes for every incoming request.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()
