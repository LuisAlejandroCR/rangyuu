# test_whep.py: WHEP signaling without a network. Covers the offer/answer exchange, the
# session Location (absolute and relative), closing, and every refusal path.

import pytest

from rangyuu.ring_client import Credentials, RingClient, RingError
from rangyuu.whep import WhepClient, WhepSession

OFFER = "v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\ns=-\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\n"
ANSWER = "v=0\r\no=- 1 1 IN IP4 127.0.0.1\r\ns=-\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\n"


class FakeTransport:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, data, headers, timeout):
        self.calls.append({"method": method, "url": url, "headers": headers, "data": data})
        return self.responses.pop(0) if self.responses else (200, {}, b"")


def client(*responses):
    ring = RingClient(Credentials(access_token="t"), transport=lambda *a: (200, b"{}"))
    return WhepClient(ring, transport=FakeTransport(*responses))


def test_open_sends_the_offer_as_sdp_and_returns_the_answer():
    whep = client((201, {"Location": "https://api.amazonvision.com/v1/whep/sessions/s1"}, ANSWER.encode()))
    session = whep.open("dev-1", OFFER)
    call = whep.transport.calls[0]
    assert call["method"] == "POST" and call["data"] == OFFER.encode()
    assert call["headers"]["Content-Type"] == "application/sdp"
    assert call["headers"]["Authorization"] == "Bearer t"
    assert "/v1/devices/dev-1/media/streaming/whep/sessions" in call["url"]
    assert session.answer == ANSWER and session.status == 201 and session.closable


def test_a_relative_location_is_resolved_against_the_request():
    whep = client((201, {"location": "/v1/whep/sessions/s2"}, ANSWER.encode()))
    assert whep.open("dev-1", OFFER).location == "https://api.amazonvision.com/v1/whep/sessions/s2"


def test_a_session_without_location_cannot_be_closed_and_says_so():
    whep = client((200, {}, ANSWER.encode()))
    session = whep.open("dev-1", OFFER)
    assert not session.closable and whep.close(session) is False


def test_close_sends_delete_to_the_session_url():
    whep = client((201, {"Location": "https://api.amazonvision.com/s1"}, ANSWER.encode()), (204, {}, b""))
    session = whep.open("dev-1", OFFER)
    assert whep.close(session) is True
    assert whep.transport.calls[-1]["method"] == "DELETE"
    assert whep.transport.calls[-1]["url"] == "https://api.amazonvision.com/s1"


@pytest.mark.parametrize("offer", ["empty", "not-sdp", "none", "oversized"])
def test_a_malformed_offer_never_reaches_the_network(offer):
    values = {"empty": "", "not-sdp": "not an sdp", "none": None, "oversized": "v=0" + "a" * 300_000}
    whep = client()
    with pytest.raises(RingError):
        whep.open("dev-1", values[offer])
    assert whep.transport.calls == []


def test_a_refusal_raises_instead_of_returning_a_half_open_session():
    whep = client((403, {}, b"forbidden"))
    with pytest.raises(RingError) as error:
        whep.open("dev-1", OFFER)
    assert "403" in str(error.value)


def test_a_non_sdp_body_is_refused():
    whep = client((200, {}, b'{"error":"nope"}'))
    with pytest.raises(RingError):
        whep.open("dev-1", OFFER)


def test_plaintext_session_urls_are_refused():
    ring = RingClient(Credentials(access_token="t"), transport=lambda *a: (200, b"{}"))
    whep = WhepClient(ring, base_url="http://api.example.com", transport=FakeTransport())
    with pytest.raises(RingError):
        whep.open("dev-1", OFFER)
    with pytest.raises(RingError):
        whep.close(WhepSession("dev-1", ANSWER, "http://api.example.com/s1", 201))
