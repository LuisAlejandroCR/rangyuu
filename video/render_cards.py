# render_cards.py: renders video/cards.html to MP4 (1920x1080, 30 fps, no audio) and the small Tilo
# clips in video/tilo_overlay.html to MOV with alpha (480x400, qtrle) for compositing.
# Usage: python video/render_cards.py [test]   -> media/cards/, or test PNGs at chosen times.
# Tilo's SVGs come from docs/brand/tilo/, or from the docs/tilo-mascot branch until PR #10 is merged.
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "media" / "cards"
FPS = 30
TEST_TIMES = {"supervised": [0.3, 1.2, 2.3, 3.9], "end": [0.5, 1.5, 2.1, 2.9],
              "peek_up": [0.3, 2.0], "peek_side": [0.3, 2.0], "sit": [0.3, 2.75]}


def encode(page, clip, dur, path, alpha):
    if alpha:
        codec = ["-c:v", "qtrle", "-pix_fmt", "argb"]
    else:
        codec = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16"]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe",
                           "-framerate", str(FPS), "-c:v", "png", "-i", "-"] + codec + [str(path)],
                          stdin=subprocess.PIPE)
    for i in range(round(dur * FPS)):
        page.evaluate("([c, t]) => render(c, t)", [clip, i / FPS])
        ff.stdin.write(page.screenshot(type="png", omit_background=alpha))
    ff.stdin.close()
    ff.wait()
    print(clip, "->", path)


def run(page, html, args, alpha, test):
    page.goto((ROOT / "video" / html).as_uri())
    page.evaluate("(a) => setup(...a)", args)
    for clip, dur in page.evaluate("window.DURATION").items():
        if test:
            for t in TEST_TIMES[clip]:
                page.evaluate("([c, t]) => render(c, t)", [clip, t])
                page.screenshot(path=str(OUT / f"{clip}_t{t}.png"), omit_background=alpha)
        else:
            encode(page, clip, dur, OUT / (f"tilo_{clip}.mov" if alpha else f"{clip}.mp4"), alpha)


def tilo_svg(name):
    local = ROOT / "docs" / "brand" / "tilo" / name
    if local.exists():
        return local.read_text(encoding="utf-8")
    return subprocess.run(["git", "show", f"origin/docs/tilo-mascot:docs/brand/tilo/{name}"],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def main():
    test = len(sys.argv) > 1 and sys.argv[1] == "test"
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        front, rest = tilo_svg("tilo-front.svg"), tilo_svg("tilo-rest.svg")
        for html, size, args, alpha in [("cards.html", (1920, 1080), [front, rest], False),
                                        ("tilo_overlay.html", (480, 400), [front], True)]:
            page = browser.new_page(viewport={"width": size[0], "height": size[1]})
            page.on("pageerror", lambda e: print("[page error]", e))
            run(page, html, args, alpha, test)
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
