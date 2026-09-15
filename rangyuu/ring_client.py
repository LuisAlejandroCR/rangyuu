# ring_client.py: read-only client for the Ring API. Resolves the bearer token (Playground
# access token, or refresh-token exchange when the app is registered) and exposes device
# discovery. It never logs a credential and never falls back to plaintext HTTP.

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import urlparse

from . import config

BASE_URL = "https://api.amazonvision.com"
TIMEOUT = 10.0
REFRESH_MARGIN = 60.0
MAX_BODY = 1_048_576


class RingError(RuntimeError):
    """Raised for every failure. The message never carries a token or a secret."""


def _https(url: str, name: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RingError(f"{name} must be an https URL")
    return url.rstrip("/")


@dataclass
class Credentials:
    """What the process has available. Values come from the environment, never from a payload."""

    access_token: str = ""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    token_url: str = ""

    @classmethod
    def from_env(cls) -> "Credentials":
        return cls(
            access_token=config.get("RING_ACCESS_TOKEN"),
            client_id=config.get("RING_CLIENT_ID"),
            client_secret=config.get("RING_CLIENT_SECRET"),
            refresh_token=config.get("RING_REFRESH_TOKEN"),
            token_url=config.get("RING_TOKEN_URL"),
        )

    @property
    def can_refresh(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token and self.token_url)

    def __repr__(self) -> str:  # keeps secrets out of tracebacks and logs
        return (f"Credentials(access_token={'set' if self.access_token else 'unset'}, "
                f"client_id={'set' if self.client_id else 'unset'}, can_refresh={self.can_refresh})")


class RingClient:
    def __init__(self, credentials=None, *, base_url=BASE_URL, transport=None, clock=time.time):
        self.credentials = credentials or Credentials.from_env()
        self.base_url = _https(base_url, "base_url")
        self.transport = transport or _urlopen
        self.clock = clock
        self._token = self.credentials.access_token
        self._expires_at = float("inf") if self._token else 0.0

    # --- auth ------------------------------------------------------------

    def token(self) -> str:
        """Return a usable bearer token, refreshing it when it is about to expire."""
        if self._token and self.clock() < self._expires_at - REFRESH_MARGIN:
            return self._token
        if not self.credentials.can_refresh:
            if self._token:
                return self._token
            raise RingError("no usable credentials: set RING_ACCESS_TOKEN, or the four RING_* values "
                            "needed to refresh")
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.credentials.refresh_token,
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
        }
        body = self._request("POST", _https(self.credentials.token_url, "RING_TOKEN_URL"), payload)
        token = body.get("access_token")
        expires_in = body.get("expires_in")
        if not isinstance(token, str) or not token.strip():
            raise RingError("token response did not contain an access_token")
        if isinstance(expires_in, (int, float)) and expires_in > 0:
            self._expires_at = self.clock() + float(expires_in)
        else:
            self._expires_at = self.clock() + 1800.0
        if isinstance(body.get("refresh_token"), str) and body["refresh_token"].strip():
            self.credentials.refresh_token = body["refresh_token"]
        self._token = token
        return token

    # --- read-only endpoints ---------------------------------------------

    def devices(self) -> list:
        found = self._get("/v1/devices")
        items = found.get("devices", found) if isinstance(found, dict) else found
        return items if isinstance(items, list) else []

    def device_status(self, device_id: str) -> dict:
        return self._get(f"/v1/devices/{_device(device_id)}/status")

    def capabilities(self, device_id: str) -> dict:
        return self._get(f"/v1/devices/{_device(device_id)}/capabilities")

    def me(self) -> dict:
        return self._get("/v1/users/me")

    # --- transport --------------------------------------------------------

    def _get(self, path: str) -> dict:
        return self._request("GET", f"{self.base_url}{path}", None, self.token())

    def _request(self, method: str, url: str, payload=None, token: str = "") -> dict:
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            status, raw = self.transport(method, url, data, headers, TIMEOUT)
        except urllib.error.HTTPError as error:  # pragma: no cover - exercised through transport
            raise RingError(f"ring responded {error.code}") from None
        except OSError:
            raise RingError("ring is unreachable") from None
        if status == 401:
            raise RingError("ring rejected the credentials (401)")
        if status >= 400:
            raise RingError(f"ring responded {status}")
        if len(raw) > MAX_BODY:
            raise RingError("response too large")
        try:
            value = json.loads(raw or b"{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RingError("ring returned invalid json") from None
        return value if isinstance(value, (dict, list)) else {}


def _device(device_id: str) -> str:
    if not isinstance(device_id, str) or not device_id.strip() or "/" in device_id or "?" in device_id:
        raise RingError("invalid device id")
    return device_id.strip()


def _urlopen(method, url, data, headers, timeout):  # pragma: no cover - network path
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read(MAX_BODY + 1)
