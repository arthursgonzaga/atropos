import pytest
from pydantic import ValidationError
from models import AlertPayload, AlertResponse


def test_valid_alert_payload():
    p = AlertPayload(status="empty", device="ender3_v3_se")
    assert p.status == "empty"
    assert p.device == "ender3_v3_se"


def test_invalid_status_raises():
    with pytest.raises(ValidationError):
        AlertPayload(status="full", device="ender3_v3_se")


def test_missing_device_raises():
    with pytest.raises(ValidationError):
        AlertPayload(status="empty")


def test_alert_response():
    r = AlertResponse(received=True)
    assert r.received is True
