"""Manually authored timeline of (scene, time_range) -> (object, action, zone).

Since the camera follows the action rather than staying fixed on one wide
shot, zones/actions can't be derived from bounding-box position alone. This
timeline was built from the person recording the footage describing what
happens and when in each clip.

Times are in seconds, [start, end) within each scene's video.
"""

# actor is assumed "patient" unless a scene explicitly involves the caregiver
TIMELINE = {
    "scene1_placement": [
        {"start": 0.0, "end": 2.0, "object": "glasses", "action": "placed", "zone": "table", "actor": "patient"},
        {"start": 2.0, "end": 6.0, "object": "medicine box", "action": "placed", "zone": "table", "actor": "patient"},
        {"start": 6.0, "end": 8.0, "object": "keys", "action": "placed", "zone": "key holder", "actor": "patient"},
        {"start": 8.0, "end": 12.0, "object": "remote", "action": "placed", "zone": "remote holder", "actor": "patient"},
        {"start": 12.0, "end": 15.6, "object": "mug", "action": "placed", "zone": "living room table", "actor": "patient"},
    ],
    "scene2_pickup_move": [
        # glasses: table -> book shelf (pick up from table, then placed on shelf)
        {"start": 0.0, "end": 3.0, "object": "glasses", "action": "picked_up", "zone": "table", "actor": "patient"},
        {"start": 3.0, "end": 6.0, "object": "glasses", "action": "placed", "zone": "book shelf", "actor": "patient"},
        # remote: table -> remote holder
        {"start": 6.0, "end": 8.5, "object": "remote", "action": "picked_up", "zone": "table", "actor": "patient"},
        {"start": 8.5, "end": 11.0, "object": "remote", "action": "placed", "zone": "remote holder", "actor": "patient"},
        # medicine box: table -> refrigerator
        {"start": 11.0, "end": 18.0, "object": "medicine box", "action": "picked_up", "zone": "table", "actor": "patient"},
        {"start": 18.0, "end": 25.5, "object": "medicine box", "action": "placed", "zone": "refrigerator", "actor": "patient"},
    ],
    "scene3_handoff": [
        # caregiver pulls medicine box from fridge and gives it to patient
        {"start": 0.0, "end": 6.0, "object": "medicine box", "action": "picked_up", "zone": "refrigerator", "actor": "caregiver"},
        {"start": 6.0, "end": 13.4, "object": "medicine box", "action": "handed_over", "zone": "living room", "actor": "caregiver"},
    ],
    "scene4_filler": [
        # no tracked objects intentionally handled; used to test false-positive robustness
    ],
}
