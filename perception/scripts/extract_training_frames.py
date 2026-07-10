"""Densely extract frames from scene1/scene2 footage for YOLOv8 fine-tune labeling."""
import cv2
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw_footage"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "labeled" / "images"
FRAME_STEP = 3  # save every Nth frame (denser than the 0.5s sampling used elsewhere)
SOURCE_SCENES = ["scene1_placement.mp4", "scene2_pickup_move.mp4", "handsoff.mp4"]


def extract(video_path: Path, out_dir: Path, frame_step: int = FRAME_STEP):
    cap = cv2.VideoCapture(str(video_path))
    scene_name = video_path.stem

    frame_idx = 0
    saved = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % frame_step == 0:
            out_name = f"{scene_name}_tf{saved:04d}.jpg"
            cv2.imwrite(str(out_dir / out_name), frame)
            saved += 1
        frame_idx += 1

    cap.release()
    print(f"{scene_name}: extracted {saved} training frames -> {out_dir}")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for scene_file in SOURCE_SCENES:
        video_path = RAW_DIR / scene_file
        if not video_path.exists():
            print(f"Missing: {video_path}")
            continue
        extract(video_path, OUT_DIR)
