# test_ring_client.py: the Ring client without a network. A fake transport records what would
# be sent, so token refresh, error mapping and credential hygiene are testable with no account.

import json

import pytest

from rangyuu.ring_client import Credentials, RingClient, RingError

TOKEN_URL = "https://auth.example.com/token"


class FakeTransport:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, data, headers, timeout):
        self.calls.append({"method": method, "url": url, "headers": headers,
                           "body": json.loads(data) if data else None})
        status, payload = self.responses.pop(0) if self.responses else (200, {})
        return status, json.dumps(payload).encode()


def refreshable(**changes):
    values = dict(client_id="cid", client_secret="secret", refresh_token="r1", token_url=TOKEN_URL)
    values.update(changes)
    return Credentials(**values)


def test_access_token_is_used_as_is_and_never_refreshed():
    transport = FakeTransport((200, {"devices": [{"id": "d1"}]}))
    client = RingClient(Credentials(access_token="playground"), transport=transport)
    assert client.devices() == [{"id": "d1"}]
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer playground"


def test_refresh_token_is_exchanged_and_reused_until_it_nears_expiry():
    transport = FakeTransport((200, {"access_token": "t1", "expires_in": 1800}), (200, {"devices": []}),
                              (200, {"devices": []}))
    now = [1_000.0]
    client = RingClient(refreshable(), transport=transport, clock=lambda: now[0])
    client.devices()
    now[0] += 100
    client.devices()
    assert sum(1 for call in transport.calls if call["url"] == TOKEN_URL) == 1
    assert transport.calls[0]["body"]["grant_type"] == "refresh_token"


def test_token_is_refreshed_again_once_it_expires():
    transport = FakeTransport((200, {"access_token": "t1", "expires_in": 120}), (200, {"devices": []}),
                              (200, {"access_token": "t2", "expires_in": 120}), (200, {"devices": []}))
    now = [1_000.0]
    client = RingClient(refreshable(), transport=transport, clock=lambda: now[0])
    client.devices()
    now[0] += 200
    client.devices()
    assert sum(1 for call in transport.calls if call["url"] == TOKEN_URL) == 2
    assert transport.calls[-1]["headers"]["Authorization"] == "Bearer t2"


def test_a_rotated_refresh_token_is_kept():
    transport = FakeTransport((200, {"access_token": "t1", "expires_in": 60, "refresh_token": "r2"}),
                              (200, {"devices": []}))
    client = RingClient(refreshable(), transport=transport)
    client.devices()
    assert client.credentials.refresh_token == "r2"


def test_without_credentials_the_error_says_what_is_missing():
    client = RingClient(Credentials(), transport=FakeTransport())
    with pytest.raises(RingError) as error:
        client.devices()
    assert "RING_ACCESS_TOKEN" in str(error.value)


def test_http_errors_are_mapped_and_never_leak_the_token():
    transport = FakeTransport((401, {"error": "bad token"}))
    client = RingClient(Credentials(access_token="s3cr3t"), transport=transport)
    with pytest.raises(RingError) as error:
        client.devices()
    assert "401" in str(error.value) and "s3cr3t" not in str(error.value)


def test_credentials_repr_hides_every_secret():
    text = repr(refreshable(access_token="s3cr3t"))
    assert "s3cr3t" not in text and "secret" not in text.replace("client_secret", "")


def test_plaintext_endpoints_are_refused():
    with pytest.raises(RingError):
        RingClient(Credentials(access_token="t"), base_url="http://api.example.com")
    client = RingClient(refreshable(token_url="http://auth.example.com/token"), transport=FakeTransport())
    with pytest.raises(RingError):
        client.devices()


@pytest.mark.parametrize("device_id", ["", "   ", "a/b", "a?b", None])
def test_invalid_device_ids_never_reach_the_network(device_id):
    transport = FakeTransport()
    client = RingClient(Credentials(access_token="t"), transport=transport)
    with pytest.raises(RingError):
        client.device_status(device_id)
    assert transport.calls == []


def test_invalid_json_is_reported_as_such():
    class Broken(FakeTransport):
        def __call__(self, *args):
            return 200, b"<html>"

    client = RingClient(Credentials(access_token="t"), transport=Broken())
    with pytest.raises(RingError):
        client.me()
