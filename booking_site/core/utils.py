from typing import Any

from fastapi import Depends, Cookie, HTTPException
from httpx import AsyncClient
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from booking_site.core.config import API_URL, oauth2_scheme, templates


async def ac():
    async with AsyncClient(base_url=API_URL) as client:
        yield client


def get_token(request: Request):
    auth_token = request.cookies.get("auth_token")
    if auth_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return auth_token


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def page(request: Request, name: str, message: str = "", data: Any = None):
    return templates.TemplateResponse(name, {"request": request, "message": message, "data": data})


def redirect(url: str, message: str = ""):
    separator = "&" if "?" in url else "?"
    return RedirectResponse(f"{url}{separator}message={message}", status_code=status.HTTP_303_SEE_OTHER)