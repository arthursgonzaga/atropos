import json

import httpx
import respx
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@respx.mock
def test_alert_pauses_print_and_sends_notification():
    respx.post("http://octoprint.local/api/job").mock(return_value=httpx.Response(204))
    respx.post("http://synapse.local/message").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    r = client.post(
        "/v1/filament/alert",
        json={"status": "empty", "device": "ender3_v3_se"},
    )
    assert r.status_code == 200
    assert r.json() == {"received": True}


@respx.mock
def test_alert_sends_critical_notification_when_octoprint_unreachable():
    respx.post("http://octoprint.local/api/job").mock(
        side_effect=httpx.ConnectError("refused")
    )
    synapse_route = respx.post("http://synapse.local/message").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    r = client.post(
        "/v1/filament/alert",
        json={"status": "empty", "device": "ender3_v3_se"},
    )
    assert r.status_code == 200
    assert r.json() == {"received": True}
    body = json.loads(synapse_route.calls.last.request.content)
    assert "CRÍTICO" in body["text"]


@respx.mock
def test_alert_sends_critical_notification_when_octoprint_returns_500():
    respx.post("http://octoprint.local/api/job").mock(
        return_value=httpx.Response(500)
    )
    synapse_route = respx.post("http://synapse.local/message").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    r = client.post(
        "/v1/filament/alert",
        json={"status": "empty", "device": "ender3_v3_se"},
    )
    assert r.status_code == 200
    body = json.loads(synapse_route.calls.last.request.content)
    assert "CRÍTICO" in body["text"]


def test_alert_invalid_status_returns_422():
    r = client.post(
        "/v1/filament/alert",
        json={"status": "full", "device": "ender3_v3_se"},
    )
    assert r.status_code == 422


def test_alert_missing_body_returns_422():
    r = client.post("/v1/filament/alert", json={})
    assert r.status_code == 422


def test_alert_wrong_content_type_returns_422():
    r = client.post("/v1/filament/alert", data="not-json")
    assert r.status_code == 422
