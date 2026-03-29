import uuid
from typing import List

from pydantic import BaseModel, ConfigDict

from booking_site.rooms.schemas import RoomSimpleResponseSchema


class HotelCreateSchema(BaseModel):
    name: str
    description: str
    rating: int
    country: str
    city: str
    street: str
    house_number: str


class HotelUpdateSchema(BaseModel):
    id: uuid.UUID
    description: str
    rating: int


class HotelSimpleResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    rating: int
    country: str
    city: str
    street: str
    house_number: str

    model_config = ConfigDict(from_attributes=True)


class HotelFullResponseSchema(HotelSimpleResponseSchema):
    rooms_schemas : List[RoomSimpleResponseSchema]
