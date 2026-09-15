# __main__.py: the visible consumer, offline. Replays a Ring fixture through the same
# normalizer and spatial state the HTTP boundary uses, and prints what the rover would be told.
# Run: python -m rangyuu [ruta/al/fixture.json]

import json
import sys
from pathlib import Path

from .api import RingApiState, _normalize_event

FIXTURE = "tests/fixtures/b0_events.json"
IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
MAX_AGE = 30.0


def main(argv) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    path = argv[1] if len(argv) > 1 else FIXTURE
    events = json.loads(Path(path).read_text(encoding="utf-8"))
    devices = {event["device_id"] for event in events}
    state = RingApiState("demo-secret", calibrations=dict.fromkeys(devices, IDENTITY), max_age=MAX_AGE)

    clock, device = 0.0, next(iter(devices))
    for event in events:
        normalized = _normalize_event(event)
        clock, device = normalized["timestamp"], normalized["device_id"]
        accepted, mapped = state.register(event)
        _report(state, device, clock, f"{event.get('type')} - aceptado={accepted} mapeado={mapped}")

    _report(state, device, clock + MAX_AGE + 1, "sin eventos nuevos; la observacion caduco")
    return 0


def _cell(state, device_id):
    """The most recently observed cell for that device; that is the one the rover is asking about."""
    observed = [o for (device, _), o in state.spatial.cells.items() if device == device_id]
    return list(max(observed, key=lambda o: o.observed_at).cell) if observed else [0, 0]


def _report(state, device_id, clock, note) -> None:
    report = state.spatial.evaluate_trajectory(device_id, clock, [_cell(state, device_id)])
    print(f"[t={clock:>12.0f}] {note}")
    print("                " + json.dumps(report, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
