# =================================================================
# detector/views.py  —  Django Views (replaces Flask routes)
# =================================================================
#
# Flask → Django mapping:
#
#   @app.route("/")                  →  def index_view(request)
#   @app.route("/detect", POST)      →  def detect_view(request)
#   render_template("index.html")    →  render(request, "detector/index.html")
#   jsonify({...})                   →  JsonResponse({...})
#   request.files["image"]           →  request.FILES["image"]
#   file.save(path)                  →  open(path,"wb") + file.chunks()
# =================================================================

import os
import uuid
import base64
import datetime

import cv2
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Access the model loaded once in apps.py ready()
from .apps import DetectorConfig

# -----------------------------------------------------------------
# Storage folders (inside detector/static/detector/ so Django's
# staticfiles system can serve them automatically in development)
# -----------------------------------------------------------------
UPLOAD_FOLDER  = os.path.join(
    settings.BASE_DIR, "detector", "static", "detector", "uploads"
)
RESULTS_FOLDER = os.path.join(
    settings.BASE_DIR, "detector", "static", "detector", "results"
)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

# Create folders on startup if they don't exist yet
os.makedirs(UPLOAD_FOLDER,  exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


# -----------------------------------------------------------------
# Helper: validate file extension
# -----------------------------------------------------------------
def allowed_file(filename: str) -> bool:
    """Return True if filename has an allowed image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -----------------------------------------------------------------
# Helper: run YOLOv8 inference and draw bounding boxes
# Identical logic to Flask version's detect_objects()
# -----------------------------------------------------------------
def detect_objects(image_path: str, result_save_path: str) -> dict:
    """
    Run YOLOv8 on the image at image_path.

    Returns dict with:
        result_image_b64  — base64 JPEG string for inline display
        result_filename   — filename of saved result (for download)
        detections        — list of {class_name, confidence, bbox}
        total             — number of objects detected
        class_summary     — {class_name: count}
    """
    model        = DetectorConfig.yolo_model
    coco_classes = DetectorConfig.coco_classes
    colors       = DetectorConfig.colors

    # 1. Read image as BGR numpy array
    img_bgr = cv2.imread(image_path)

    # 2. Run YOLOv8 inference (conf=0.25 → 25% minimum confidence)
    results = model(img_bgr, conf=0.25)
    result  = results[0]

    detections    = []
    class_summary = {}

    # 3. Draw bounding boxes for every detection
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        confidence = float(box.conf[0])
        class_id   = int(box.cls[0])
        class_name = coco_classes[class_id]

        color = tuple(int(c) for c in colors[class_id])
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, 2)

        label = f"{class_name} {confidence:.0%}"
        (text_w, text_h), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
        )
        cv2.rectangle(img_bgr, (x1, y1 - text_h - 8), (x1 + text_w + 4, y1), color, -1)
        cv2.putText(
            img_bgr, label, (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA,
        )

        detections.append({
            "class_name": class_name,
            "confidence": round(confidence * 100, 2),
            "bbox":       [x1, y1, x2, y2],
        })
        class_summary[class_name] = class_summary.get(class_name, 0) + 1

    # 4. Save annotated result image to disk
    cv2.imwrite(result_save_path, img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 92])

    # 5. Encode as base64 for inline JSON transfer (no second HTTP request)
    _, buffer = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
    b64_image = base64.b64encode(buffer).decode("utf-8")

    return {
        "result_image_b64": b64_image,
        "result_filename":  os.path.basename(result_save_path),
        "detections":       detections,
        "total":            len(detections),
        "class_summary":    class_summary,
    }


# =================================================================
# VIEW 1 — Homepage  GET /
# Flask:  @app.route("/")  →  return render_template("index.html")
# Django: render(request, "detector/index.html")
# =================================================================
def index_view(request):
    return render(request, "detector/index.html")


# =================================================================
# VIEW 2 — Detection endpoint  POST /detect/
# Flask:  @app.route("/detect", methods=["POST"])
# Django: @csrf_exempt + if request.method != "POST": ...
#
# Key Django differences from Flask:
#   request.FILES["image"]  instead of  request.files["image"]
#   JsonResponse({...})     instead of  jsonify({...})
#   file.chunks()           to write uploaded bytes to disk
# =================================================================
@csrf_exempt   # Disable CSRF for this API endpoint so fetch() works
def detect_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Only POST allowed"}, status=405)

    # Guard: image field must be present
    if "image" not in request.FILES:
        return JsonResponse({"success": False, "error": "No image file provided"}, status=400)

    uploaded_file = request.FILES["image"]

    if not uploaded_file.name:
        return JsonResponse({"success": False, "error": "No file selected"}, status=400)

    if not allowed_file(uploaded_file.name):
        return JsonResponse({"success": False, "error": "File type not allowed"}, status=400)

    # Save original upload to static/detector/uploads/
    # Django's uploaded file doesn't have .save(path) — write chunks manually
    ext         = uploaded_file.name.rsplit(".", 1)[1].lower()
    unique_id   = uuid.uuid4().hex
    upload_name = f"upload_{unique_id}.{ext}"
    upload_path = os.path.join(UPLOAD_FOLDER, upload_name)

    with open(upload_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    # NOTE: original is kept permanently — never deleted (same as Flask version)

    # Build timestamped path for annotated result
    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_name = f"result_{timestamp}_{unique_id[:8]}.jpg"
    result_path = os.path.join(RESULTS_FOLDER, result_name)

    # Run YOLOv8 detection
    try:
        output = detect_objects(upload_path, result_path)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": True, **output})
