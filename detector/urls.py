# =================================================================
# detector/urls.py  —  URL Patterns for the Detector App
# =================================================================
#
# Flask equivalent:
#     @app.route("/")                        → index_view
#     @app.route("/detect", methods=["POST"])→ detect_view
#
# In Django, routes are declared as a list of path() calls.
# =================================================================

from django.urls import path
from . import views

app_name = "detector"

urlpatterns = [
    # GET /  →  render index.html (the main upload page)
    path("", views.index_view, name="index"),

    # POST /detect/  →  run YOLOv8 and return JSON
    # ⚠ Note the trailing slash — Django's CommonMiddleware adds it.
    #   The JS fetch() call must use "/detect/" (not "/detect").
    path("detect/", views.detect_view, name="detect"),
]
