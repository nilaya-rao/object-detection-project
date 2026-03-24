# =================================================================
# object_detect_django/urls.py  —  Root URL Configuration
# =================================================================
# Django reads this file first for every incoming request and
# routes it to the correct app.
#
# Flask equivalent:
#   app = Flask(__name__)          ← Django handles this internally
#   All routes are in detector/urls.py (included below)
# =================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel at http://localhost:8000/admin/
    path("admin/", admin.site.urls),

    # Delegate everything else to the detector app's own urls.py
    # "" means the detector app owns the root path "/"
    path("", include("detector.urls")),
]

# Serve static files (CSS/JS/images) in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR)
