"""Build a YOLOv8 train/val dataset from data/labeled/{to_label,labels} and write data.yaml.

Only includes images that have a non-empty label file (at least one box),
since empty-everywhere images add little value for a small fine-tune and
YOLO will otherwise treat them as pure background negatives.
"""
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_SRC = ROOT / "data" / "labeled" / "to_label"
LABELS_SRC = ROOT / "data" / "labeled" / "labels"
CLASSES_FILE = ROOT / "data" / "labeled" / "classes.txt"
DATASET_DIR = ROOT / "data" / "dataset"
VAL_RATIO = 0.15
SEED = 42


def main():
    classes = [l.strip() for l in CLASSES_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]

    # Only keep images with at least one non-empty label
    usable = []
    for label_path in sorted(LABELS_SRC.glob("*.txt")):
        content = label_path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        img_path = None
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = IMAGES_SRC / f"{label_path.stem}{ext}"
            if candidate.exists():
                img_path = candidate
                break
        if img_path:
            usable.append((img_path, label_path))

    if not usable:
        print("No labeled images found. Run the labeler first.")
        return

    random.seed(SEED)
    random.shuffle(usable)
    n_val = max(1, round(len(usable) * VAL_RATIO))
    val_set = usable[:n_val]
    train_set = usable[n_val:]

    for split_name, split_set in [("train", train_set), ("val", val_set)]:
        img_out = DATASET_DIR / "images" / split_name
        lbl_out = DATASET_DIR / "labels" / split_name
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        for img_path, label_path in split_set:
            shutil.copy(img_path, img_out / img_path.name)
            shutil.copy(label_path, lbl_out / label_path.name)

    yaml_content = (
        f"path: {DATASET_DIR.as_posix()}\n"
        f"train: images/train\n"
        f"val: images/val\n"
        f"nc: {len(classes)}\n"
        f"names: {classes}\n"
    )
    (DATASET_DIR / "data.yaml").write_text(yaml_content, encoding="utf-8")

    print(f"Train images: {len(train_set)}")
    print(f"Val images: {len(val_set)}")
    print(f"Dataset written to: {DATASET_DIR}")
    print(f"data.yaml:\n{yaml_content}")


if __name__ == "__main__":
    main()
