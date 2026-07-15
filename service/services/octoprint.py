import httpx
from config import get_settings


async def pause_print() -> None:
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.octoprint_url}/api/job",
            headers={
                "X-Api-Key": settings.octoprint_api_key,
                "Content-Type": "application/json",
            },
            json={"command": "pause", "action": "pause"},
            timeout=10.0,
        )
        response.raise_for_status()
