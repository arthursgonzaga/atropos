import json

import httpx
import pytest
import respx

from services.octoprint import pause_print


@respx.mock
async def test_pause_print_sends_correct_request():
    route = respx.post("http://octoprint.local/api/job").mock(
        return_value=httpx.Response(204)
    )
    await pause_print()
    assert route.called
    request = route.calls.last.request
    assert request.headers["X-Api-Key"] == "test-api-key"
    assert request.headers["Content-Type"] == "application/json"
    body = json.loads(request.content)
    assert body == {"command": "pause", "action": "pause"}


@respx.mock
async def test_pause_print_raises_on_http_error():
    respx.post("http://octoprint.local/api/job").mock(
        return_value=httpx.Response(500)
    )
    with pytest.raises(httpx.HTTPStatusError):
        await pause_print()


@respx.mock
async def test_pause_print_raises_on_connection_error():
    respx.post("http://octoprint.local/api/job").mock(
        side_effect=httpx.ConnectError("refused")
    )
    with pytest.raises(httpx.ConnectError):
        await pause_print()
