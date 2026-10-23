# run_redacted.py: runs a Ring script for a screen recording with the token loaded from .env.local
# in-process (never on screen, in a log or in a visible argument) and every device ID, session ID
# and IP address masked before it reaches the terminal. Usage: python run_redacted.py <script> [args]
import os
import re
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASK = "[hidden]"


def token():
    for line in (ROOT / ".env.local").read_text(encoding="utf-8").splitlines():
        if line.startswith("RANGYUU_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("RANGYUU_ACCESS_TOKEN is not set in .env.local")


class Redacting:
    """Masks secrets and identifiers in everything written to the terminal."""

    def __init__(self, stream, secrets):
        self.stream, self.secrets = stream, [s for s in secrets if s]
        self.patterns = [
            re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),                       # IPv4
            re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}\b"),                # UUID-like ids
            re.compile(r"(devices/|sessions/)[^/\s'\"]+"),                      # ids inside URLs
            re.compile(r"(\(|\bid['\"]?:\s*['\"]?)[A-Za-z0-9_\-:.]{6,}"),       # "(id)" and id: fields
        ]

    def write(self, text):
        for secret in self.secrets:
            text = text.replace(secret, MASK)
        for pattern in self.patterns:
            text = pattern.sub(lambda m: (m.group(1) if m.groups() else "") + MASK, text)
        return self.stream.write(text)

    def flush(self):
        self.stream.flush()


def main():
    script, args = sys.argv[1], sys.argv[2:]
    secret = token()
    os.environ["RANGYUU_ACCESS_TOKEN"] = secret
    sys.path.insert(0, str(ROOT))
    device_ids = []
    try:
        from rangyuu.ring_client import RingClient
        device_ids = [d.get("id", "") for d in RingClient().devices()]
    except Exception:
        pass
    sys.stdout = Redacting(sys.stdout, [secret] + device_ids)
    sys.stderr = Redacting(sys.stderr, [secret] + device_ids)
    if script == "-c":
        exec(compile(args[0], "<shot>", "exec"), {"__name__": "__main__"})
        return
    sys.argv = [script, "--token", secret] + args
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
