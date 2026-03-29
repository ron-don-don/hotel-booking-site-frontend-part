import uuid
from datetime import datetime
from typing import Tuple, List

from pydantic import BaseModel, Field, ConfigDict


class RoomCreateSchema(BaseModel):
    number: int
    prestige: str
    fine: float

    is_available: bool = Field(default=True)

    hotel_id: uuid.UUID


class RoomUpdateSchema(BaseModel):
    id: uuid.UUID

    prestige: str
    fine: float

    is_available: bool


class RoomSimpleResponseSchema(RoomUpdateSchema):
    number: int
    model_config = ConfigDict(from_attributes=True)


class RoomFullResponseSchema(RoomSimpleResponseSchema):
    booking_dates: List[Tuple[datetime, datetime]]