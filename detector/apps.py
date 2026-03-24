# =================================================================
# detector/apps.py  —  App Configuration + Model Loading
# =================================================================
# Flask loads the model at module level (runs once when app.py
# is imported):
#
#     model = YOLO("yolov8n.pt")          ← Flask
#
# Django's equivalent is AppConfig.ready(), which Django calls
# exactly once after all apps are loaded.  We store the model
# as class-level attributes so views.py can access it.
# =================================================================

import os
import numpy as np
from django.apps import AppConfig


class DetectorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "detector"

    # Class-level attributes — shared across all requests
    # (set in ready(), read in views.py)
    yolo_model    = None   # YOLO model instance
    coco_classes  = None   # {0: 'person', 1: 'bicycle', ...}
    colors        = None   # NumPy array: BGR colour per class index

    def ready(self):
        """
        Called once by Django when the server starts.

        Django's dev server uses an auto-reloader that forks a child
        process; RUN_MAIN is only set in that child, so we guard
        against loading the model twice.
        """
        # Only load in the actual server process, not the reloader watcher
        if os.environ.get("RUN_MAIN") != "true":
            return

        from ultralytics import YOLO

        print("🔍 Loading YOLOv8 model …")
        DetectorConfig.yolo_model   = YOLO("yolov8n.pt")
        DetectorConfig.coco_classes = DetectorConfig.yolo_model.names

        # Deterministic colour palette — same class always gets same colour
        np.random.seed(42)
        DetectorConfig.colors = np.random.randint(
            0, 255,
            size=(len(DetectorConfig.coco_classes), 3),
            dtype=np.uint8,
        )
        print("✅ YOLOv8 model loaded successfully")
