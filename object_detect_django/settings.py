# =================================================================
# object_detect_django/settings.py  —  Django Project Configuration
# =================================================================
import os
from pathlib import Path

# BASE_DIR = the project root (folder that contains manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------
# Security
# -----------------------------------------------------------------
SECRET_KEY  = "django-insecure-object_detect_django-yolov8-detection-key-2024"
DEBUG       = True
ALLOWED_HOSTS = ["*"]          # allow all hosts in development

# -----------------------------------------------------------------
# Installed apps
# -----------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "detector",                  # ← our YOLOv8 detection app
]

# -----------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "object_detect_django.urls"

# -----------------------------------------------------------------
# Templates
# APP_DIRS=True → Django looks inside each app's templates/ folder
# Our template lives at:  detector/templates/detector/index.html
# -----------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND":  "django.template.backends.django.DjangoTemplates",
        "DIRS":     [],
        "APP_DIRS": True,
        "OPTIONS":  {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "object_detect_django.wsgi.application"

# -----------------------------------------------------------------
# Database  (SQLite — only needed by Django admin/auth, not detection)
# -----------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   BASE_DIR / "db.sqlite3",
    }
}

# -----------------------------------------------------------------
# Static files
# Django's staticfiles system serves files from each app's static/
# folder automatically when DEBUG=True.
# Our uploads/results live inside detector/static/detector/
# -----------------------------------------------------------------
STATIC_URL = "/static/"

# -----------------------------------------------------------------
# Upload size limits  (raise Django's 2.5 MB default to 16 MB)
# -----------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024 * 1024   # 16 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 16 * 1024 * 1024   # 16 MB

# -----------------------------------------------------------------
# Misc
# -----------------------------------------------------------------
LANGUAGE_CODE      = "en-us"
TIME_ZONE          = "UTC"
USE_I18N           = True
USE_TZ             = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
