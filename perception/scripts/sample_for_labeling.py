"""Sample a spaced-out subset of training frames to upload to Roboflow for labeling."""
import shutil
from pathlib import Path

IMAGES_DIR = Path(__file__).resolve().parent.parent / "data" / "labeled" / "images"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "labeled" / "to_label"
SAMPLE_STEP = 3  # take every 3rd frame to reduce near-duplicates


def main():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    all_images = sorted(IMAGES_DIR.glob("*.jpg"))
    sampled = all_images[::SAMPLE_STEP]

    for img_path in sampled:
        shutil.copy(img_path, SAMPLE_DIR / img_path.name)

    print(f"Sampled {len(sampled)} of {len(all_images)} frames -> {SAMPLE_DIR}")
    print("Upload the contents of this folder to Roboflow for labeling.")


if __name__ == "__main__":
    main()
