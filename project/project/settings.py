# =============================================================================
# FILE: project/settings.py
# -----------------------------------------------------------------------------
# PURPOSE:  The single configuration file for the whole Django project. It
#           defines which apps run, how the database is reached, where templates
#           and static/media files live, authentication behaviour, and security
#           settings.
# ROLE:     Loaded by Django at startup (manage.py / wsgi.py / asgi.py set
#           DJANGO_SETTINGS_MODULE=project.settings). It also reads the local
#           '.env' file so secrets and DB details live outside the source code.
# =============================================================================

# --- Imports -----------------------------------------------------------------
import os
from pathlib import Path

# PyMySQL is a pure-Python MySQL driver. install_as_MySQLdb() makes it masquerade
# as Django's expected "MySQLdb" module, so the MySQL backend works even when the
# native mysqlclient package can't be compiled (common on Windows). Wrapped in
# try/except so the project still starts if PyMySQL isn't installed.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR is the absolute path to the 'project' folder (the one containing
# manage.py), so all file locations below are relative to the project root.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Environment (.env) loader -----------------------------------------------
# Django has no built-in .env support, so this small helper reads a simple
# KEY=VALUE file and puts each value into the process environment. os.environ
# .setdefault is used so a value already present in the real environment wins
# (never overwrites existing settings). Returns nothing.
def load_env_file(path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        # Skip blank lines, comments, and any line without an '=' separator.
        if not line or line.startswith('#') or '=' not in line:
            continue
        # Split only on the first '=' so values may themselves contain '='.
        key, value = line.split('=', 1)
        # Trim whitespace and any surrounding single/double quotes from the value.
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# Load the .env file (if present) so the settings below can read from it.
load_env_file(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Used for cryptographic signing (sessions, password resets, CSRF). Falls back to
# a hard-coded development key when SECRET_KEY isn't set in the environment.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-0^%f5h0^kn1m-5hm1oc=0$j9+z*bf8-t^av1f&^no*4tz2abt7')

# SECURITY WARNING: don't run with debug turned on in production!
# True enables detailed error pages and auto-reload during development.
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Hosts/domains the site may serve. Read from ALLOWED_HOSTS as a comma-separated
# list; protects against HTTP Host header attacks. Defaults to local addresses.
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]


# Application definition

# INSTALLED_APPS: every Django "app" (and built-in component) that is active.
# The django.contrib.* entries are Django's built-in features (admin, auth,
# sessions, messages, static-file handling). 'app.apps.AppConfig' is this
# project's own application (see app/apps.py).
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.apps.AppConfig',
]

# MIDDLEWARE: a stack of hooks that process every request/response. Order matters.
#  - SecurityMiddleware:       basic security headers.
#  - SessionMiddleware:        enables server-side sessions.
#  - CommonMiddleware:         URL normalisation, ETags, etc.
#  - CsrfViewMiddleware:       blocks cross-site request forgery on forms.
#  - AuthenticationMiddleware: attaches the logged-in user to each request.
#  - MessageMiddleware:        enables the one-time flash messages used in views.
#  - XFrameOptionsMiddleware:  clickjacking protection (see X_FRAME_OPTIONS).
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# The module Django loads first to route incoming URLs. Points at project/urls.py.
ROOT_URLCONF = 'project.urls'

# TEMPLATES: configures the Django template engine.
#  - DIRS: extra template folders to search (a project-level 'templates' folder).
#  - APP_DIRS=True: also look inside each app's own 'templates' folder (this is
#    where app/templates/*.html lives).
#  - context_processors: values injected into EVERY template automatically
#    (request, the current user, messages, debug info).
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # project-level templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI entry point used by the development server and WSGI deployments.
WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# NOTE: This block is hard-coded to SQLite and does NOT read the DB_ENGINE /
# DB_NAME / DB_USER / ... values from .env. So despite README.md and
# .env.example describing MySQL, the app actually runs on a local SQLite file
# (db.sqlite3) in the project root unless this block is changed by hand.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

# Use this project's custom user model (with phone + user_type role) instead of
# Django's default User. Defined in app/models.py as CustomUser.
AUTH_USER_MODEL = 'app.CustomUser'

# Rules enforced when a user sets/changes a password:
#  - UserAttributeSimilarityValidator: password can't be too similar to the user.
#  - MinimumLengthValidator:              enforces a minimum length.
#  - CommonPasswordValidator:             rejects well-known common passwords.
#  - NumericPasswordValidator:            rejects all-numeric passwords.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'   # Default language for the site.

TIME_ZONE = 'UTC'         # Time zone used to display/store datetimes.

USE_I18N = True           # Enable Django's translation machinery.

USE_TZ = True             # Store timezone-aware datetimes in the database.


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'   # URL prefix used to reference static files in templates.

# Extra folders (besides each app's static folder) that 'collectstatic' should
# scan. Here it points at the project-root 'static' folder (static/css, static/js).
STATICFILES_DIRS = [BASE_DIR / "static"]

# Destination folder where 'collectstatic' gathers all static files for
# production. This is build output and is git-ignored.
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'     # URL prefix for user-uploaded files (images, logos...).

MEDIA_ROOT = BASE_DIR / 'media'   # Filesystem folder where uploads are stored.

# --- Authentication flow -----------------------------------------------------
# Named URL to send unauthenticated users to when a view requires login.
LOGIN_URL = 'login'
# Where to land after a successful login; 'dashboard_redirect' then forwards the
# user to the dashboard matching their role (buyer/agent/broker).
LOGIN_REDIRECT_URL = 'dashboard_redirect'
# Where to go after logging out.
LOGOUT_REDIRECT_URL = 'login'
# Session lifetime: 60*60*8 = 8 hours of inactivity before the session expires.
SESSION_COOKIE_AGE = 60 * 60 * 8
# Expire the session cookie when the browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Allow JavaScript to read the CSRF cookie (False = readable by JS). Lower
# security, but matches how some pages here post forms via scripts.
CSRF_COOKIE_HTTPONLY = False
# Turn on the browser's reflected-XSS filter as an extra defence.
SECURE_BROWSER_XSS_FILTER = True
# Forbid this site from being displayed inside an <iframe>/<frame> (clickjacking).
X_FRAME_OPTIONS = 'DENY'
