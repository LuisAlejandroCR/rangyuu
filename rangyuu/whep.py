# whep.py: WHEP signaling for Ring live view. Sends the SDP offer, keeps the session
# Location and closes it with DELETE. Signaling only: decoding the media is a separate
# concern (B10), so this module stays dependency-free and testable without a network.

import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from .ring_client import BASE_URL, RingError, TIMEOUT, _device

SESSION_PATH = "/v1/devices/{device_id}/media/streaming/whep/sessions"
SDP_TYPE = "application/sdp"
MAX_SDP = 262_144


@dataclass
class WhepSession:
    """An open live-view session: the answer to feed a peer connection, and how to close it."""

    device_id: str
    answer: str
    location: str
    status: int

    @property
    def closable(self) -> bool:
        return bool(self.location)


class WhepClient:
    def __init__(self, client, *, base_url=BASE_URL, transport=None):
        self.client = client
        self.base_url = base_url.rstrip("/")
        self.transport = transport or _urlopen

    def open(self, device_id: str, offer: str) -> WhepSession:
        """POST the SDP offer and return the session. A non-2xx answer raises, never half-opens."""
        if not isinstance(offer, str) or not offer.startswith("v=0"):
            raise RingError("offer must be an SDP string")
        if len(offer) > MAX_SDP:
            raise RingError("offer too large")
        url = self.base_url + SESSION_PATH.format(device_id=_device(device_id))
        headers = {"Authorization": f"Bearer {self.client.token()}",
                   "Content-Type": SDP_TYPE, "Accept": SDP_TYPE}
        status, response_headers, body = self._send("POST", url, offer.encode(), headers)
        if status >= 400:
            raise RingError(f"ring refused the whep session ({status})")
        answer = body.decode("utf-8", "replace")
        if not answer.startswith("v=0"):
            raise RingError("ring did not return an SDP answer")
        return WhepSession(device_id, answer, _location(response_headers, url), status)

    def close(self, session: WhepSession) -> bool:
        """Always call this: an abandoned session keeps counting against the account's limit."""
        if not session.closable:
            return False
        headers = {"Authorization": f"Bearer {self.client.token()}"}
        status, _, _ = self._send("DELETE", session.location, None, headers)
        return status < 400

    def _send(self, method, url, data, headers):
        if urlparse(url).scheme != "https":
            raise RingError("whep endpoints must be https")
        try:
            return self.transport(method, url, data, headers, TIMEOUT)
        except urllib.error.HTTPError as error:  # pragma: no cover - exercised through transport
            return error.code, dict(error.headers or {}), error.read(MAX_SDP)
        except OSError:
            raise RingError("ring is unreachable") from None


def _location(headers, request_url: str) -> str:
    """Resolve the session Location, which the spec allows to be relative to the request."""
    found = ""
    for key, value in (headers or {}).items():
        if key.lower() == "location" and isinstance(value, str):
            found = value.strip()
            break
    return urljoin(request_url, found) if found else ""


def _urlopen(method, url, data, headers, timeout):  # pragma: no cover - network path
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, dict(response.headers), response.read(MAX_SDP)
