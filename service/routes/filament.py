import logging

from fastapi import APIRouter

from models import AlertPayload, AlertResponse
from services.notifier import send_alert
from services.octoprint import pause_print

router = APIRouter()
logger = logging.getLogger(__name__)

_ALERT_MSG = (
    "⚠️ Alerta Ender 3 V3 SE: O filamento acabou! "
    "Impressão pausada automaticamente."
)
_CRITICAL_MSG = (
    "🚨 CRÍTICO: Falha ao tentar pausar a Ender 3 V3 SE! "
    "O OctoPrint está inacessível. Verifique a impressora imediatamente!"
)


@router.post("/v1/filament/alert", response_model=AlertResponse)
async def filament_alert(payload: AlertPayload) -> AlertResponse:
    try:
        await pause_print()
        await send_alert(_ALERT_MSG)
    except Exception as exc:
        logger.error("Failed to pause print: %s", exc, exc_info=True)
        try:
            await send_alert(_CRITICAL_MSG)
        except Exception as notify_exc:
            logger.error("Failed to send critical alert: %s", notify_exc, exc_info=True)
    return AlertResponse(received=True)
