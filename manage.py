#!/usr/bin/env python
"""
manage.py — Django command-line utility.
Usage:
    python manage.py runserver          → start on http://localhost:8000
    python manage.py runserver 0.0.0.0:8000  → accessible on local network
    python manage.py migrate            → set up the database
"""
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "object_detect_django.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed:\n"
            "    pip install django"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()