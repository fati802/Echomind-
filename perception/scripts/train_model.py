"""Fine-tune YOLOv8n on the EchoMind object dataset.

Resumes from the most recent round's best.pt if it exists, otherwise
starts from the base pretrained COCO weights (round 1).
"""
from pathlib import Path
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
DATA_YAML = ROOT / "data" / "dataset" / "data.yaml"
BASE_WEIGHTS = ROOT / "yolov8n.pt"

# Most recent round first; falls back through earlier rounds, then base weights.
CANDIDATE_PREV_BEST = [
    ROOT / "models" / "echomind_yolo_r2" / "weights" / "best.pt",
    ROOT / "models" / "echomind_yolo" / "weights" / "best.pt",
]
RUN_NAME = "echomind_yolo_r3"

if __name__ == "__main__":
    start_weights = BASE_WEIGHTS
    for candidate in CANDIDATE_PREV_BEST:
        if candidate.exists():
            start_weights = candidate
            break
    print(f"Starting from: {start_weights}")

    model = YOLO(str(start_weights))
    model.train(
        data=str(DATA_YAML),
        epochs=60,
        imgsz=640,
        batch=8,
        patience=15,
        project=str(ROOT / "models"),
        name=RUN_NAME,
        exist_ok=True,
    )
