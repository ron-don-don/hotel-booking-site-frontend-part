import uuid
from datetime import datetime

from pydantic import BaseModel


class BookingRequestSchema(BaseModel):
    room_id: uuid.UUID
    check_in: datetime
    check_out: datetime

class BookingResponseSchema(BaseModel):
    id: uuid.UUID
    room_id : uuid.UUID
    check_in: datetime
    check_out: datetime
    room_number : int
    room_prestige : str
    room_fine: float
    hotel_name : str
    hotel_id : uuid.UUID
