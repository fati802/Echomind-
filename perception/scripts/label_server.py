"""Minimal local labeling server: serves images from data/labeled/to_label and
saves YOLO-format bounding box labels back to data/labeled/labels on request.

Run with: python scripts/label_server.py
Then open http://localhost:8420 in a browser.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "data" / "labeled" / "to_label"
LABELS_DIR = ROOT / "data" / "labeled" / "labels"
CLASSES_FILE = ROOT / "data" / "labeled" / "classes.txt"
STATIC_HTML = Path(__file__).resolve().parent / "labeler.html"

LABELS_DIR.mkdir(parents=True, exist_ok=True)

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".html": "text/html",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # quiet

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/" or path == "/index.html":
            self._serve_file(STATIC_HTML, "text/html")
            return

        if path == "/api/images":
            images = sorted(
                p.name for p in IMAGES_DIR.iterdir()
                if p.suffix.lower() in (".jpg", ".jpeg", ".png")
            )
            labeled = {p.stem for p in LABELS_DIR.glob("*.txt")}
            self._send_json({"images": images, "labeled": sorted(labeled)})
            return

        if path == "/api/classes":
            classes = [
                line.strip()
                for line in CLASSES_FILE.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self._send_json({"classes": classes})
            return

        if path.startswith("/images/"):
            fname = path[len("/images/"):]
            img_path = IMAGES_DIR / fname
            ext = img_path.suffix.lower()
            if img_path.exists() and ext in MIME_TYPES:
                self._serve_file(img_path, MIME_TYPES[ext])
                return
            self.send_error(404)
            return

        if path.startswith("/api/label/"):
            stem = path[len("/api/label/"):]
            label_path = LABELS_DIR / f"{stem}.txt"
            if label_path.exists():
                content = label_path.read_text(encoding="utf-8")
            else:
                content = ""
            self._send_json({"content": content})
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/api/save":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            stem = data["stem"]
            lines = data["lines"]  # list of "class_idx cx cy w h" strings

            label_path = LABELS_DIR / f"{stem}.txt"
            label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            self._send_json({"status": "saved", "count": len(lines)})
            return

        self.send_error(404)

    def _serve_file(self, path: Path, mime: str):
        if not path.exists():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    port = 8420
    server = HTTPServer(("localhost", port), Handler)
    print(f"Labeling server running at http://localhost:{port}")
    print(f"Images dir: {IMAGES_DIR}")
    print(f"Labels dir: {LABELS_DIR}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
