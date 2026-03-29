import uuid

from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from starlette.requests import Request

from booking_site.core.config import ROOM_PAGE
from booking_site.core.utils import ac, auth_header, page, get_token, redirect
from booking_site.rooms.schemas import RoomCreateSchema, RoomUpdateSchema

rooms_router = APIRouter(prefix="/rooms", tags=["rooms"])


@rooms_router.get("/room/{room_id}")
async def room_page(request: Request, room_id: uuid.UUID, client: AsyncClient = Depends(ac)):
    response = await client.get(f"/rooms/room/{room_id}")
    if response.status_code == 200:
        return page(request, ROOM_PAGE, data=response.json())
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Room not found")
    raise HTTPException(status_code=500, detail="Unknown room load error")


@rooms_router.get("/{hotel_id}/rooms")
async def get_rooms_by_hotel_id(hotel_id: uuid.UUID, client: AsyncClient = Depends(ac)):
    response = await client.get(f"/hotels/view/{hotel_id}")
    if response.status_code == 200:
        return response.json()["rooms_schemas"]
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Hotel not found")
    raise HTTPException(status_code=500, detail="Unknown rooms load error")


@rooms_router.post("/create")
async def create_room(request: Request, room_r: RoomCreateSchema,
                      auth_token: str = Depends(get_token), client: AsyncClient = Depends(ac)):
    response = await client.post("/rooms/create", json=room_r.model_dump(mode="json"), headers=auth_header(auth_token))

    if response.status_code == 201:
        return redirect("/admin_page", message="Room created successfully")

    elif response.status_code == 409:
        return redirect("/admin_page", message="Room already exists")

    elif response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown room create error")


@rooms_router.patch("/update")
async def update_room(request: Request, room_r: RoomUpdateSchema,
                      auth_token: str = Depends(get_token), client: AsyncClient = Depends(ac)):
    response = await client.patch("/rooms/update", json=room_r.model_dump(mode="json"), headers=auth_header(auth_token))

    if response.status_code == 200:
        return redirect("/admin_page", message="Room update successfully")

    elif response.status_code == 404:
        return redirect("/admin_page", message="Room not found")

    elif response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown room update error")


@rooms_router.delete("/delete/{room_id}")
async def delete_room(request: Request, room_id: uuid.UUID, auth_token: str = Depends(get_token),
                      client: AsyncClient = Depends(ac)):
    response = await client.delete(f"/rooms/delete/{room_id}", headers=auth_header(auth_token))

    if response.status_code == 200:
        return redirect("/admin_page", message="Room delete successfully")

    elif response.status_code == 404:
        return redirect("/admin_page", message="Room not found")

    elif response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown room delete error")