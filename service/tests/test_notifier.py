import json

import httpx
import pytest
import respx

from services.notifier import send_alert


@respx.mock
async def test_send_alert_posts_to_synapse():
    route = respx.post("http://synapse.local/message").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )
    await send_alert("test message")
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["text"] == "test message"
    assert body["chat_id"] == "123456789"


@respx.mock
async def test_send_alert_raises_on_failure():
    respx.post("http://synapse.local/message").mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(httpx.HTTPStatusError):
        await send_alert("test message")
