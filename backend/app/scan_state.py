"""In-memory buffer for the most recent card scan.

The hardware reader (ESP32) and the human-facing screen (web dashboard) are
two separate devices. The reader POSTs a UID to /cards/scan; the screen polls
/cards/last-scan to learn what was just presented. This module is the bridge
between them.

`seq` is a monotonically increasing counter: the screen remembers the last seq
it handled and reacts only when it changes, so an old scan is never replayed.

Single-process (one uvicorn worker) in-memory state — intentional for the demo.
It resets on restart and is not shared across workers; a multi-worker or
multi-station deployment would move this to Redis / a table keyed by station.
"""
from threading import Lock

_lock = Lock()
_state = {"seq": 0, "uid": None, "known": False, "patient_id": None}


def record_scan(uid: str, known: bool, patient_id: int | None) -> None:
    with _lock:
        _state["seq"] += 1
        _state["uid"] = uid
        _state["known"] = known
        _state["patient_id"] = patient_id


def get_last_scan() -> dict:
    with _lock:
        return dict(_state)
