import base64
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from httpx import AsyncClient
from starlette.requests import Request

from booking_site.core.config import HOTEL_DEFAULT_IMAGE, HOTELS_PAGE, HOTEL_PAGE
from booking_site.core.utils import ac, auth_header, page, get_token, redirect
from booking_site.hotels.schemas import HotelCreateSchema, HotelUpdateSchema

hotels_router = APIRouter(prefix="/hotels", tags=["hotels"])


@hotels_router.get("/view")
async def hotels_page(request: Request, client: AsyncClient = Depends(ac)):
    response = await client.get("/hotels/view")
    if response.status_code == 200:
        return page(request, HOTELS_PAGE, data=response.json())
    raise HTTPException(status_code=500, detail="Unknown hotel load error")


@hotels_router.get("/view/{hotel_id}")
async def hotel_page(request: Request, hotel_id: uuid.UUID, client: AsyncClient = Depends(ac)):
    response = await client.get(f"/hotels/view/{hotel_id}")
    if response.status_code == 200:
        image = await client.get(f"/hotels/image/{hotel_id}")
        if image.status_code == 200:
            return page(request, HOTEL_PAGE,
                        data={"image": base64.b64encode(image.content).decode(), "hotel": response.json()})
        else:
            return page(request, HOTEL_PAGE, data={"image": HOTEL_DEFAULT_IMAGE, "hotel": response.json()})
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Hotel not found")
    raise HTTPException(status_code=500, detail="Unknown hotel load error")

@hotels_router.post("/create")
async def create_hotel(request: Request, hotel_r: HotelCreateSchema,
                       auth_token: str = Depends(get_token), client: AsyncClient = Depends(ac)):
    response = await client.post("/hotels/create", json=hotel_r.model_dump(mode="json"),
                                 headers=auth_header(auth_token))

    if response.status_code == 201:
        return redirect("/admin_page", message="Hotel created successfully")

    elif response.status_code == 409:
        return redirect("/admin_page", message="Hotel already exists")

    elif response.status_code == 401:
        return redirect("/admin_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown hotel create error")


@hotels_router.patch("/update")
async def update_hotel(request: Request, hotel_r: HotelUpdateSchema,
                       auth_token: str = Depends(get_token), client: AsyncClient = Depends(ac)):
    response = await client.patch("/hotels/update", json=hotel_r.model_dump(mode="json"),
                                  headers=auth_header(auth_token))

    if response.status_code == 200:
        return redirect("/admin_page", message="Hotel updated successfully")

    elif response.status_code == 404:
        return redirect("/admin_page", message="Hotel not found")

    elif response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown hotel update error")


@hotels_router.delete("/delete/{hotel_id}")
async def delete_hotel(request: Request, hotel_id: uuid.UUID, auth_token: str = Depends(get_token),
                       client: AsyncClient = Depends(ac)):
    response = await client.delete(f"/hotels/delete/{hotel_id}", headers=auth_header(auth_token))

    if response.status_code == 200:
        return redirect("/admin_page", message="Hotel deleted successfully")

    elif response.status_code == 404:
        return redirect("/admin_page", message="Hotel not found")

    elif response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown hotel delete error")


@hotels_router.post("/image/{hotel_id}")
async def create_image(request: Request, hotel_id: uuid.UUID, image: UploadFile, auth_token: str = Depends(get_token),
                       client: AsyncClient = Depends(ac)):
    response = await client.post(f"/hotels/image/{hotel_id}",
                                 files={"image": (image.filename, await image.read(), image.content_type)},
                                 headers=auth_header(auth_token))

    if response.status_code == 201:
        return redirect("/admin_page", message="Hotel image created successfully")

    elif response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown hotel image create error")


@hotels_router.delete("/image/{hotel_id}")
async def delete_image(request: Request, hotel_id: uuid.UUID, auth_token: str = Depends(get_token),
                       client: AsyncClient = Depends(ac)):
    response = await client.delete(f"/hotels/image/{hotel_id}", headers=auth_header(auth_token))

    if response.status_code == 200:
        return redirect("/admin_page", message="Hotel image deleted successfully")

    elif response.status_code == 404:
        return redirect("/admin_page", message="Hotel image not found")

    elif response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid admin credentials")

    return redirect("/admin_page", message="Unknown hotel image delete error")
