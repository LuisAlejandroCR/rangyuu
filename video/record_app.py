# record_app.py: records the real local app (http://localhost:8080) in English through Chrome's
# CDP screencast (real frames at 2x, with their timestamps), for the demo's app shots. Modes:
# tour (shot 4: Now, a tapped cell, On board with the camera off, System), watch <seconds>
# (shot 5A: the screen while the server is stopped elsewhere), go (the closing GO). Writes media/captures/app_<mode>.mp4 and a JSON log of timestamps.
import base64
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media" / "captures"
URL = os.environ.get("RANGYUU_URL", "http://localhost:8080")
PHONE = {"width": 430, "height": 932}


def state(page):
    return page.inner_text("#verdict-state")


def tour(page, log):
    page.wait_for_function("document.getElementById('verdict-state').textContent === 'GO'", timeout=15000)
    log.append(("now", time.time())); page.wait_for_timeout(4000)
    page.locator("#map-now").scroll_into_view_if_needed(); page.wait_for_timeout(1500)
    # The map redraws on every refresh, so click where the cell is rather than a node that may go.
    box = page.locator("#map-now rect.cell[data-cell='3,2']").bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.locator("#cell-detail").scroll_into_view_if_needed()
    log.append(("cell", time.time())); page.wait_for_timeout(4500)
    page.mouse.wheel(0, -2000); page.wait_for_timeout(600)
    page.click(".tabs button[data-goto='caminata']")
    log.append(("onboard", time.time())); page.wait_for_timeout(4000)
    page.click(".tabs button[data-goto='sistema']")
    log.append(("system", time.time())); page.wait_for_timeout(3000)
    page.mouse.wheel(0, 500); page.wait_for_timeout(3000)


def watch(page, log, seconds):
    page.wait_for_function("document.getElementById('verdict-state').textContent === 'GO'", timeout=15000)
    page.click(".tabs button[data-goto='ahora']")          # the gesture that lets alerts sound
    log.append(("go", time.time()))
    end = time.time() + seconds
    seen = "GO"
    while time.time() < end:
        now = state(page)
        if now != seen:
            log.append((now, time.time())); seen = now
        page.wait_for_timeout(200)


class Screencast:
    """Collects the page's real frames from CDP and encodes them with their own timing."""

    def __init__(self, context, page, folder):
        self.folder, self.frames = folder, []
        folder.mkdir(parents=True, exist_ok=True)
        self.cdp = context.new_cdp_session(page)
        self.cdp.on("Page.screencastFrame", self._frame)
        self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "everyNthFrame": 1})

    def _frame(self, event):
        path = self.folder / f"{len(self.frames):05d}.jpg"
        path.write_bytes(base64.b64decode(event["data"]))
        self.frames.append((path, event["metadata"]["timestamp"]))
        self.cdp.send("Page.screencastFrameAck", {"sessionId": event["sessionId"]})

    def stop(self, target):
        self.cdp.send("Page.stopScreencast")
        listing = self.folder / "frames.txt"
        rows = []
        for (path, at), (_, nxt) in zip(self.frames, self.frames[1:] + [(None, None)]):
            rows.append(f"file '{path.name}'\nduration {((nxt - at) if nxt else 0.5):.3f}")
        rows.append(f"file '{self.frames[-1][0].name}'")
        listing.write_text("\n".join(rows), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                        "-vf", "fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "16", str(target)], check=True)
        return self.frames[0][1]


def main():
    mode = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / f"_{mode}"
    shutil.rmtree(tmp, ignore_errors=True)
    log = [("start", time.time())]
    target = OUT / f"app_{mode}.mp4"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport=PHONE, device_scale_factor=2, locale="en-US")
        page = context.new_page()
        clips = []
        page.on("request", lambda r: clips.append((r.url.split("/voices/")[-1], time.time())) if "/voices/" in r.url else None)
        page.goto(URL, wait_until="networkidle")
        cast = Screencast(context, page, tmp)
        log.append(("recording", time.time()))
        if mode == "tour":
            tour(page, log)
        elif mode == "watch":
            watch(page, log, float(sys.argv[2]))
        elif mode == "go":
            page.wait_for_function("document.getElementById('verdict-state').textContent === 'GO'", timeout=15000)
            page.wait_for_timeout(6000)
        first = cast.stop(target)
        context.close(); browser.close()
    shutil.rmtree(tmp, ignore_errors=True)
    (OUT / f"app_{mode}.json").write_text(json.dumps({"first_frame_epoch": first, "log": log, "clips": clips}, indent=1), encoding="utf-8")
    print(target, log)


if __name__ == "__main__":
    main()
