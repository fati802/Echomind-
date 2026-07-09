"""Run pretrained YOLOv8 over extracted frames to gauge baseline detection quality."""
from pathlib import Path
from ultralytics import YOLO
from collections import defaultdict

FRAMES_DIR = Path(__file__).resolve().parent.parent / "data" / "frames"
CONF_THRESHOLD = 0.25

# Classes relevant to EchoMind (COCO names)
RELEVANT_CLASSES = {"cup", "remote", "wine glass", "handbag", "backpack", "book", "bottle", "cell phone", "person"}

model = YOLO("yolov8n.pt")

summary = defaultdict(lambda: defaultdict(int))

for scene_dir in sorted(FRAMES_DIR.iterdir()):
    if not scene_dir.is_dir():
        continue
    frames = sorted(scene_dir.glob("*.jpg"))
    for frame_path in frames:
        results = model.predict(str(frame_path), conf=CONF_THRESHOLD, verbose=False)
        for r in results:
            for box in r.boxes:
                cls_name = model.names[int(box.cls)]
                conf = float(box.conf)
                summary[scene_dir.name][cls_name] += 1

print("\n=== Detection summary per scene (pretrained YOLOv8n, conf>=0.25) ===")
for scene, counts in summary.items():
    print(f"\n{scene}:")
    for cls_name, count in sorted(counts.items(), key=lambda x: -x[1]):
        marker = " <-- relevant" if cls_name in RELEVANT_CLASSES else ""
        print(f"  {cls_name}: {count} detections{marker}")
