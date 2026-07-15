import httpx
from config import get_settings


async def send_alert(text: str) -> None:
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.synapse_url}/message",
            json={"text": text, "chat_id": settings.telegram_chat_id},
            timeout=10.0,
        )
        response.raise_for_status()
