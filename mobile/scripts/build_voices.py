# build_voices.py: turn the raw ElevenLabs takes into the clips bundled in mobile/assets/voices.
# Multi-phrase takes are split on silence; per-phrase takes are only trimmed. Every clip is peak-
# normalised to the same level and re-encoded as 64 kbps mono MP3, so both voices play equally loud.
# The raw takes are not versioned (they are regenerated, not edited). Needs: pip install miniaudio
# lameenc. Usage, from the folder holding voices/raw/: python build_voices.py <out_root>
import sys
from array import array
from pathlib import Path

import lameenc
import miniaudio

KEYS = ["proceed", "caution", "hold", "unknown", "linkLost", "start", "stop"]
RATE = 44100
PEAK = 0.89  # about -1 dBFS
RAW = Path("voices/raw")

# (voice, lang) -> either a single take holding the seven phrases in KEYS order, or a folder of
# one file per key.
SOURCES = {
    ("lumina", "es"): RAW / "es_lumina.mp3",
    ("lumina", "en"): RAW / "en_lumina.mp3",
    ("lumina", "pt"): RAW / "pt_lumina.mp3",
    ("carlos", "es"): RAW / "es_carlos.mp3",
    ("carlos", "en"): RAW / "carlos_en",
    ("carlos", "pt"): RAW / "carlos_pt",
}


def decode(path: Path) -> array:
    return miniaudio.decode_file(
        str(path), output_format=miniaudio.SampleFormat.SIGNED16, nchannels=1, sample_rate=RATE
    ).samples


def segments(samples: array, merge_gap_s: float = 1.2) -> list[tuple[int, int]]:
    """Speech spans in samples. The loudness gate is relative to this take's own peak."""
    win = RATE // 100
    env = [max(map(abs, samples[i:i + win])) for i in range(0, len(samples) - win, win)]
    gate = max(env) * 0.08
    spans, start, quiet = [], None, 0
    for i, level in enumerate(env):
        if level > gate:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet >= merge_gap_s * 100:
                spans.append((start, i - quiet))
                start, quiet = None, 0
    if start is not None:
        spans.append((start, len(env) - quiet))
    spans = [s for s in spans if s[1] - s[0] >= 15]
    return [(max(a * win - int(0.08 * RATE), 0), min(b * win + int(0.2 * RATE), len(samples))) for a, b in spans]


def encode(samples: array) -> bytes:
    peak = max(map(abs, samples)) or 1
    gain = PEAK * 32767 / peak
    scaled = array("h", (max(-32768, min(32767, int(s * gain))) for s in samples))
    enc = lameenc.Encoder()
    enc.set_bit_rate(64)
    enc.set_in_sample_rate(RATE)
    enc.set_channels(1)
    enc.set_quality(2)
    return enc.encode(scaled.tobytes()) + enc.flush()


def main() -> None:
    out_root = Path(sys.argv[1])
    for (voice, lang), src in SOURCES.items():
        out = out_root / voice / lang
        out.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            clips = {}
            for key in KEYS:
                s = decode(src / f"{key}.mp3")
                spans = segments(s, merge_gap_s=10)  # one phrase: only trim the ends
                a, b = spans[0][0], spans[-1][1]
                clips[key] = s[a:b]
        else:
            s = decode(src)
            spans = segments(s)
            if len(spans) != len(KEYS):
                sys.exit(f"{voice}/{lang}: expected {len(KEYS)} phrases, found {len(spans)}")
            clips = {key: s[a:b] for key, (a, b) in zip(KEYS, spans)}
        for key, samples in clips.items():
            data = encode(samples)
            (out / f"{key}.mp3").write_bytes(data)
            print(f"{voice}/{lang}/{key}.mp3  {len(samples) / RATE:.2f}s  {len(data)} B")


if __name__ == "__main__":
    main()
