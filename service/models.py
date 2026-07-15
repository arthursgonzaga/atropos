from typing import Literal
from pydantic import BaseModel


class AlertPayload(BaseModel):
    status: Literal["empty"]
    device: str


class AlertResponse(BaseModel):
    received: bool
