# =============================================================================
# FILE: app/__init__.py
# -----------------------------------------------------------------------------
# PURPOSE:  Marks the 'app' directory as a Python package so Django can discover
#           and import this application.
# NOTE:     This runs when the app package is first imported. It forces the
#           pure-Python PyMySQL driver to act as Django's "MySQLdb" module (a
#           fallback for the native mysqlclient). settings.py does the same thing
#           inside a try/except; here it is NOT guarded, so importing the app
#           would fail if PyMySQL were missing.
# =============================================================================
import pymysql
pymysql.install_as_MySQLdb()