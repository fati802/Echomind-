from datetime import datetime, timedelta

MOVEMENT_THRESHOLD = 40
GONE_FRAME_GAP = 20
MIN_EVENTS_FOR_PICKUP = 2


def _centroid(det):
    return (
        det["bbox_x"] + det["bbox_width"] / 2,
        det["bbox_y"] + det["bbox_height"] / 2,
    )


def _distance(c1, c2):
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5


def _base_event(obj_name, action, det, ts):
    return {
        "object": obj_name,
        "action": action,
        "actor": None,
        "zone": None,
        "timestamp": ts,
        "confidence": det["confidence"],
        "source_frame": str(det["frame"]),
        "track_id": None,
        "bbox_x": det["bbox_x"],
        "bbox_y": det["bbox_y"],
        "bbox_width": det["bbox_width"],
        "bbox_height": det["bbox_height"],
    }


def generate_events(detections: list, fps: float = 30.0, total_frames: int = None, base_time: datetime = None):
    if base_time is None:
        base_time = datetime.utcnow()

    by_object = {}
    for det in detections:
        by_object.setdefault(det["object"], []).append(det)

    if total_frames is None:
        total_frames = max((d["frame"] for d in detections), default=0)

    events = []

    for obj_name, dets in by_object.items():
        dets = sorted(dets, key=lambda d: d["frame"])
        prev = None

        for det in dets:
            ts = base_time + timedelta(seconds=det["frame"] / fps)

            if prev is None:
                events.append(_base_event(obj_name, "placed", det, ts))
            else:
                frame_gap = det["frame"] - prev["frame"]
                dist = _distance(_centroid(prev), _centroid(det))

                if frame_gap > GONE_FRAME_GAP:
                    events.append(_base_event(obj_name, "picked_up", prev, ts))
                    events.append(_base_event(obj_name, "placed", det, ts))
                elif dist > MOVEMENT_THRESHOLD:
                    events.append(_base_event(obj_name, "moved", det, ts))

            prev = det

        if total_frames - prev["frame"] > GONE_FRAME_GAP and len(dets) >= MIN_EVENTS_FOR_PICKUP:
            ts = base_time + timedelta(seconds=prev["frame"] / fps)
            events.append(_base_event(obj_name, "picked_up", prev, ts))

    return events