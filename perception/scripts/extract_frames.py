"""Extract frames from raw footage at a fixed interval for detection/labeling."""
import cv2
import os
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw_footage"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "frames"
INTERVAL_SEC = 0.5  # sample every 0.5s


def extract(video_path: Path, out_dir: Path, interval_sec: float = INTERVAL_SEC):
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    frame_interval = max(1, round(fps * interval_sec))

    scene_name = video_path.stem
    scene_out = out_dir / scene_name
    scene_out.mkdir(parents=True, exist_ok=True)

    frame_idx = 0
    saved = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % frame_interval == 0:
            timestamp_sec = frame_idx / fps
            out_name = f"{scene_name}_f{saved:04d}_t{timestamp_sec:.2f}s.jpg"
            cv2.imwrite(str(scene_out / out_name), frame)
            saved += 1
        frame_idx += 1

    cap.release()
    print(f"{scene_name}: extracted {saved} frames -> {scene_out}")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    videos = sorted(RAW_DIR.glob("*.mp4"))
    if not videos:
        print(f"No .mp4 files found in {RAW_DIR}")
    for video in videos:
        extract(video, OUT_DIR)
