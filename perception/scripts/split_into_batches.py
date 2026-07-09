"""Split the to_label images into numbered folders of 10 for easy manual upload to Roboflow."""
import shutil
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "data" / "labeled" / "to_label"
BATCH_ROOT = Path(__file__).resolve().parent.parent / "data" / "labeled" / "upload_batches"
BATCH_SIZE = 10


def main():
    images = sorted(SRC_DIR.glob("*.jpg"))
    if not images:
        print(f"No images found in {SRC_DIR}")
        return

    if BATCH_ROOT.exists():
        shutil.rmtree(BATCH_ROOT)
    BATCH_ROOT.mkdir(parents=True)

    for i, img in enumerate(images):
        batch_num = i // BATCH_SIZE + 1
        batch_dir = BATCH_ROOT / f"batch_{batch_num:02d}"
        batch_dir.mkdir(exist_ok=True)
        shutil.copy(img, batch_dir / img.name)

    num_batches = (len(images) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Split {len(images)} images into {num_batches} batches of up to {BATCH_SIZE} -> {BATCH_ROOT}")


if __name__ == "__main__":
    main()
