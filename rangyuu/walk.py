# walk.py: replays a walking clip through the onboard lane, as if it were the phone in hand.
# It exists to answer one question with a number: how often would this walk have been stopped,
# and by what. Run: python -m rangyuu.walk walking_video.mp4

import collections
import json
import sys
import time

from .onboard import CLEAR, OBSTACLE, UNCERTAIN, ForwardClearance
from .runtime import LocalRuntime
from .site import Site

IDENTITY = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
EVERY = 6                      # one reading every six frames is enough at 60 fps
ROUTE = [(2, 0), (2, 1)]


def replay(path: str, every: int = EVERY) -> dict:
    """Feed the clip to a site and report what the screen would have said, second by second."""
    import av
    import numpy as np

    runtime = LocalRuntime("iphone-onboard", IDENTITY, cell_size=0.3, max_age=600.0, stale_after=600.0)
    # El reloj del sitio sigue al video: con el reloj de pared, el replay corre 20x más rápido
    # que la caminata y la histéresis temporal dejaría de significar nada.
    video_clock = {"t": 0.0}
    site = Site(runtime, clock=lambda: video_clock["t"])
    site.set_route(ROUTE)
    site.runtime.mark_free(ROUTE, now=0.0)
    site.runtime.last_frame_at = 0.0

    container = av.open(path)
    stream = container.streams.video[0]
    states = collections.Counter()
    screens = collections.Counter()
    transitions = []
    seen = 0
    previous = None

    for index, frame in enumerate(container.decode(stream)):
        if index % every:
            continue
        video_clock["t"] = index / float(stream.average_rate)
        gray = np.asarray(frame.to_image().convert("L"), dtype=np.float32)
        result = site.observe_onboard(gray)
        state = result["clearance"]["state"]
        states[state] += 1
        screen = site.now()
        screens[screen["state"]] += 1
        seen += 1
        if screen["state"] != previous:
            transitions.append({"at_s": round(index / float(stream.average_rate), 1),
                                "screen": screen["state"], "onboard": state,
                                "reason": screen["reason"]})
            previous = screen["state"]

    return {"frames_read": seen, "onboard": dict(states), "screen": dict(screens),
            "transitions": transitions}


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("uso: python -m rangyuu.walk <video>")
        return 2
    report = replay(argv[0])
    stopped = report["screen"].get("PARA", 0)
    total = report["frames_read"] or 1
    print(json.dumps({k: report[k] for k in ("frames_read", "onboard", "screen")},
                     ensure_ascii=False, indent=1))
    print(f"\nla pantalla habría frenado en el {stopped / total:.0%} de las lecturas")
    print("\ncambios de estado:")
    for change in report["transitions"][:20]:
        print(f"  t+{change['at_s']:>5.1f}s  {change['screen']:<12} {change['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
