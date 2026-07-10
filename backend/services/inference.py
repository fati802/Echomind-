from pathlib import Path
from ultralytics import YOLO
import cv2

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
CUSTOM_MODEL_PATH = MODEL_DIR / "best.pt"
FALLBACK_MODEL = "yolov8n.pt"

_model = None

def load_model():
    global _model
    if _model is not None:
        return _model
    if CUSTOM_MODEL_PATH.exists():
        _model = YOLO(str(CUSTOM_MODEL_PATH))
        print(f"[inference] Loaded custom model: {CUSTOM_MODEL_PATH}")
    else:
        _model = YOLO(FALLBACK_MODEL)
        print(f"[inference] best.pt not found, using fallback: {FALLBACK_MODEL}")
    return _model


def process_video(video_path: str, conf_threshold: float = 0.3, frame_skip: int = 5):
    model = load_model()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    detections = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            results = model.predict(frame, conf=conf_threshold, verbose=False)
            for r in results:
                for box in r.boxes:
                    cls_name = model.names[int(box.cls)]
                    conf = float(box.conf)
                    xyxy = box.xyxy[0].tolist()
                    detections.append({
                        "object": cls_name,
                        "confidence": round(conf, 3),
                        "frame": frame_count,
                        "bbox_x": xyxy[0],
                        "bbox_y": xyxy[1],
                        "bbox_width": xyxy[2] - xyxy[0],
                        "bbox_height": xyxy[3] - xyxy[1],
                    })

        frame_count += 1

    cap.release()
    return detections, fps