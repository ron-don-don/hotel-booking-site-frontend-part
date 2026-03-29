from fastapi import APIRouter, Depends

from httpx import AsyncClient
from starlette.requests import Request

from booking_site.auth.schemas import FormSchema
from booking_site.core.config import REGISTER_PAGE, LOGIN_PAGE, ADMIN_LOGIN_PAGE
from booking_site.core.utils import ac, auth_header, page, get_token, redirect

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/register_page")
async def register_page(request: Request):
    return page(request, REGISTER_PAGE)


@auth_router.get("/login_page")
async def login_page(request: Request):
    return page(request, LOGIN_PAGE)


@auth_router.post("/login")
async def login(request: Request, data: FormSchema, client: AsyncClient = Depends(ac)):
    api_response = await client.post("/auth/login", json=data.model_dump(mode="json"))
    if api_response.status_code == 422:
        return redirect("/auth/login_page",
                        message="Invalid credentials format: username is empty or password less than 6 characters")
    elif api_response.status_code == 401:
        return redirect("/auth/login_page", message="Invalid credentials")
    elif api_response.status_code != 200:
        return redirect("/auth/login_page", message="Unknown server error, try again later")
    response = redirect("/hotels/view")
    response.set_cookie("auth_token", api_response.json()["access_token"], httponly=True)
    return response


@auth_router.post("/register")
async def register(request: Request, data: FormSchema, client: AsyncClient = Depends(ac)):
    api_response = await client.post("/auth/signup", json=data.model_dump(mode="json"))

    if api_response.status_code == 409:
        return redirect("/auth/register_page", message=f"User with username \"{data.username}\" already exists")

    elif api_response.status_code == 422:
        return redirect("/auth/register_page",
                        message="Invalid credentials format: username is empty or password less than 6 characters")

    elif api_response.status_code != 201:
        return redirect("/auth/register_page", message="Unknown server error, try again later")

    response = redirect("/", message="Registration successful!")

    token = api_response.json().get("access_token")
    response.set_cookie("auth_token", token, httponly=True)

    return response


@auth_router.post("/logout")
async def logout(request: Request, auth_token: str = Depends(get_token), client: AsyncClient = Depends(ac)):
    api_response = await client.post("/auth/logout", headers=auth_header(auth_token))

    if api_response.status_code != 200:
        return redirect("/auth/login_page", message="You should be authenticated before logout")

    response = redirect("/", message="You have successfully logged out")

    response.delete_cookie("auth_token")

    return response


@auth_router.post("/admin/login")
async def admin_login(request: Request, data: FormSchema, client: AsyncClient = Depends(ac)):
    api_response = await client.post("/auth/admin/login", json=data.model_dump(mode="json"))

    if api_response.status_code == 422:
        return redirect("/auth/admin/login_page",
                        message="Invalid credentials format: username is empty or password less than 6 characters")

    if api_response.status_code == 401:
        return redirect("/auth/admin/login_page", message="Invalid credentials")

    if api_response.status_code != 200:
        return redirect("/auth/admin/login_page", message="Unknown server error, try again later")

    response = redirect("/admin_page")

    token = api_response.json().get("access_token")
    if token:
        response.set_cookie("auth_token", token, httponly=True)

    return response


@auth_router.get("/admin/login_page")
async def admin_login_page(request: Request, message: str = "Welcome admin"):
    return page(request, ADMIN_LOGIN_PAGE, message=message)
