import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from httpx import TimeoutException, ConnectError, AsyncClient
from starlette import status
from starlette.requests import Request

import jinja2
import python_multipart

from booking_site.auth.router import auth_router
from booking_site.bookings.router import booking_router
from booking_site.core.config import ERROR_PAGE, HOME_PAGE, ADMIN_PAGE
from booking_site.core.utils import page, redirect, ac
from booking_site.hotels.router import hotels_router
from booking_site.rooms.router import rooms_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(hotels_router)
app.include_router(rooms_router)
app.include_router(booking_router)


@app.get("/")
async def home(request: Request):
    return page(request, HOME_PAGE)

@app.get("/admin_page")
async def admin_page(request: Request, client: AsyncClient = Depends(ac)):
    response = await client.get("/hotels/view")
    if response.status_code == 200:
        return page(request, ADMIN_PAGE, data=response.json())
    raise HTTPException(status_code=500, detail="Unknown hotel load error")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return redirect("/auth/login_page")
    elif exc.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
        return redirect("/error_page", message=f"422 Unprocessable Entity: {exc.detail}")
    elif exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        return redirect("/error_page", message=f"500 Internal Server Error: {exc.detail}")


@app.exception_handler(TimeoutException)
async def timeout_exception_handler(request: Request, exc: TimeoutException):
    return redirect("/error_page", message=f"500 Internal Server Error: Please, try again later")


@app.exception_handler(ConnectError)
async def connect_exception_handler(request: Request, exc: ConnectError):
    return redirect("/error_page", message="500 Internal Server Error: Please, try again later")


@app.get("/error_page")
async def error_page(request : Request, message: str):
    return page(request, ERROR_PAGE, message)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1080)