#!/usr/bin/env python
# =============================================================================
# FILE: manage.py
# -----------------------------------------------------------------------------
# PURPOSE:  Django's command-line entry point for administrative tasks. Every
#           management command (runserver, migrate, makemigrations,
#           createsuperuser, collectstatic, ...) is executed through this file.
# ROLE:     When you type "python manage.py <command>", this file tells Django
#           which settings module to use and hands control to Django's built-in
#           command-line runner.
# USED BY:  Developers/operators from a terminal (see README.md).
# DEPENDS:  The 'project.settings' module (project/project/settings.py) and
#           Django being installed in the active virtual environment.
# =============================================================================

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks.

    Ensures the DJANGO_SETTINGS_MODULE environment variable points at this
    project's settings ('project.settings'), then forwards the command-line
    arguments (sys.argv) to Django's command dispatcher.

    Raises:
        ImportError: with a helpful message if Django is not installed or the
                     virtual environment is not activated.
    """
    # Point Django at this project's settings file unless it is already set.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        # Imported lazily so a missing Django produces the clear error below
        # rather than an obscure import traceback.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Hand the terminal arguments to Django to run the requested command.
    execute_from_command_line(sys.argv)


# Standard Python idiom: only call main() when this file is run directly
# (e.g. "python manage.py runserver"), not when it is imported as a module.
if __name__ == '__main__':
    main()
