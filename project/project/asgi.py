# =============================================================================
# FILE: project/asgi.py
# -----------------------------------------------------------------------------
# PURPOSE:  ASGI (Asynchronous Server Gateway Interface) entry point. It exposes
#           the module-level 'application' callable used by ASGI servers, which
#           is required only if the project later adds asynchronous features
#           (WebSockets, long-polling, async views). For a synchronous project
#           it behaves like the WSGI entry point.
# ROLE:     Used when running under an ASGI server (e.g. Uvicorn/Daphne).
# =============================================================================
"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Point Django at the settings module, then build the ASGI application callable.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_asgi_application()
