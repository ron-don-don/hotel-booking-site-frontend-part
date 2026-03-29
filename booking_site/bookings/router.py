import uuid

from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from starlette.requests import Request

from booking_site.bookings.schemas import BookingRequestSchema
from booking_site.core.config import BOOKINGS_PAGE
from booking_site.core.utils import get_token, ac, auth_header, page, redirect

booking_router = APIRouter(prefix="/bookings", tags=["bookings"])


@booking_router.get("/all")
async def get_all_user_bookings(request: Request, token: str = Depends(get_token), client: AsyncClient = Depends(ac)):
    response = await client.get("/bookings/all", headers=auth_header(token))

    if response.status_code == 200:
        return page(request, BOOKINGS_PAGE, data=response.json())

    elif response.status_code == 401:
        return redirect("/auth/login_page", message="Please authenticate to view your bookings")

    raise HTTPException(status_code=500, detail="Unknown bookings get error")


@booking_router.post("/book")
async def book(booking_r: BookingRequestSchema, token: str = Depends(get_token),
               client: AsyncClient = Depends(ac)):
    response = await client.post("/bookings/book", headers=auth_header(token), json=booking_r.model_dump(mode="json"))

    if response.status_code == 201:
        return redirect("/bookings/all", message="Booking successful")

    elif response.status_code == 409:
        return redirect("/bookings/all", message="Booking failed")

    elif response.status_code == 401:
        return redirect("/auth/login_page", message="Please authenticate to book a room")

    return redirect("/bookings/all", message="Unknown bookings book error")


@booking_router.delete("/cancel/{booking_id}")
async def cancel_booking(booking_id: uuid.UUID, token: str = Depends(get_token), client: AsyncClient = Depends(ac)):
    response = await client.delete(f"/bookings/cancel/{booking_id}", headers=auth_header(token))

    if response.status_code == 200:
        return redirect("/bookings/all", message="Booking cancelled successfully")

    elif response.status_code == 401:
        return redirect("/auth/login_page", message="Please authenticate to cancel bookings")

    return redirect("/bookings/all", message="Unknown bookings cancel error")
