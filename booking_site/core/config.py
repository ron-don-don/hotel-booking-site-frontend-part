import base64
import os
from pathlib import Path

from dotenv import load_dotenv
import dotenv
from fastapi.security import OAuth2PasswordBearer
from starlette.templating import Jinja2Templates

DEFAULT_IMAGE_PATH = "static/images/hotel-default.jpg"
HOTEL_DEFAULT_IMAGE = ""

if os.path.exists(DEFAULT_IMAGE_PATH):
    with open(DEFAULT_IMAGE_PATH, "rb") as file:
        HOTEL_DEFAULT_IMAGE = base64.b64encode(file.read()).decode()

HOME_PAGE = "home.html"
LOGIN_PAGE = "login.html"
ADMIN_LOGIN_PAGE = "admin_login.html"
ADMIN_PAGE = "admin.html"
REGISTER_PAGE = "register.html"
HOTEL_PAGE = "hotel.html"
HOTELS_PAGE = "hotels.html"
ROOM_PAGE = "room.html"
BOOKINGS_PAGE = "bookings.html"
ACCOUNT_INFO_PAGE = "account_info.html"
ERROR_PAGE = "error.html"

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

API_URL = os.getenv("API_URL")
