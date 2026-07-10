"""Run the fine-tuned model against unseen scene3/scene4 frames to sanity-check real-world quality."""
from pathlib import Path
from ultralytics import YOLO
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "echomind_yolo_r2" / "weights" / "best.pt"
FRAMES_DIR = ROOT / "data" / "frames"
OUT_DIR = ROOT / "data" / "test_predictions"
UNSEEN_SCENES = ["scene3_handoff", "scene4_filler"]
CONF_THRESHOLD = 0.25

model = YOLO(str(MODEL_PATH))
OUT_DIR.mkdir(parents=True, exist_ok=True)

summary = defaultdict(lambda: defaultdict(int))
detection_log = []

for scene_name in UNSEEN_SCENES:
    scene_dir = FRAMES_DIR / scene_name
    if not scene_dir.exists():
        print(f"Missing: {scene_dir}")
        continue

    scene_out = OUT_DIR / scene_name
    scene_out.mkdir(parents=True, exist_ok=True)

    frames = sorted(scene_dir.glob("*.jpg"))
    for frame_path in frames:
        results = model.predict(str(frame_path), conf=CONF_THRESHOLD, verbose=False)
        for r in results:
            if len(r.boxes) > 0:
                # Save annotated image only for frames with detections
                annotated = r.plot()
                import cv2
                cv2.imwrite(str(scene_out / frame_path.name), annotated)

            for box in r.boxes:
                cls_name = model.names[int(box.cls)]
                conf = float(box.conf)
                summary[scene_name][cls_name] += 1
                detection_log.append(f"{scene_name}/{frame_path.name}: {cls_name} ({conf:.2f})")

print("\n=== Detection summary on UNSEEN scenes (fine-tuned model, conf>=0.25) ===")
for scene, counts in summary.items():
    print(f"\n{scene}:")
    if not counts:
        print("  (no detections at all)")
    for cls_name, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {cls_name}: {count} detections")

print(f"\n=== Full detection log ({len(detection_log)} total) ===")
for line in detection_log:
    print(line)

print(f"\nAnnotated frames with detections saved to: {OUT_DIR}")
