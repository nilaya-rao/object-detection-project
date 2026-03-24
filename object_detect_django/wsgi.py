# =================================================================
# object_detect_django/wsgi.py  —  WSGI entry point
# =================================================================
# Used by production servers (Gunicorn, uWSGI):
#     gunicorn object_detect_django.wsgi:application
# =================================================================
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "object_detect_django.settings")
application = get_wsgi_application()
