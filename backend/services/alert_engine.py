from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session

from backend.models.event import Event
from backend.schemas.alert import AlertResponse

# Har object ka apna threshold (minutes) — jitni dair "picked_up" reh sakta hai bina alert ke
OBJECT_THRESHOLDS_MIN: Dict[str, int] = {
    "medicine box": 60,
    "glasses": 120,
    "keys": 180,
    "wallet": 180,
}
DEFAULT_THRESHOLD_MIN = 90

RESOLVED_ACTIONS = {"placed", "returned", "put_back"}
ACTIVE_ACTIONS = {"picked_up", "removed", "taken"}


def _get_threshold(object_name: str) -> int:
    return OBJECT_THRESHOLDS_MIN.get(object_name.lower(), DEFAULT_THRESHOLD_MIN)


def generate_alerts(db: Session) -> List[AlertResponse]:
    """
    Har distinct object ka SABSE RECENT event nikalo.
    Agar wo event 'active' (picked_up/removed) hai aur threshold se zyada
    time guzar gaya hai bina 'placed' huye — alert raise karo.
    """
    alerts: List[AlertResponse] = []

    objects = db.query(Event.object).distinct().all()

    for (object_name,) in objects:
        last_event = (
            db.query(Event)
            .filter(Event.object == object_name)
            .order_by(Event.timestamp.desc())
            .first()
        )
        if not last_event:
            continue

        action = last_event.action.lower()
        if action not in ACTIVE_ACTIONS:
            continue  # object already placed/returned — sab theek hai

        elapsed_min = (datetime.now() - last_event.timestamp).total_seconds() / 60
        threshold = _get_threshold(object_name)

        if elapsed_min >= threshold:
            severity = "critical" if elapsed_min >= threshold * 2 else "warning"
            display_name = object_name.strip().capitalize()
            hours = int(elapsed_min // 60)
            mins = int(elapsed_min % 60)
            time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins} min"

            alerts.append(
                AlertResponse(
                    object=object_name,
                    actor=last_event.actor,
                    zone=last_event.zone,
                    last_action=last_event.action,
                    last_seen=last_event.timestamp,
                    minutes_elapsed=round(elapsed_min, 1),
                    message=f"You haven't put the {display_name} back yet — it's been {time_str}.",
                    severity=severity,
                )
            )

    alerts.sort(key=lambda a: a.minutes_elapsed, reverse=True)
    return alerts