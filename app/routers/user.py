from urllib import request

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse

# from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.constants import FlashCategory
from app.core.flash import set_flash, get_flash

from app.database import get_db
from app.schemas.user import UserCreate
from app.services.user_service import UserService

from app.core.template import render

router = APIRouter()
# templates = Jinja2Templates(directory="app/templates")

user_service = UserService()


@router.get("/register")
def register_page(request: Request):
    return render(
        request=request,
        template="register.html",
        title="User Registration",
    )


@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = UserCreate(username=username, email=email, password=password)

    created_user = user_service.create_user(db, user)

    if created_user is None:
        return render(
            request=request,
            template="register.html",
            title="Register",
            error="Email already exists",
        )

    # return RedirectResponse(url="/", status_code=303)
    set_flash(request, "Registration successful. Please login.", FlashCategory.SUCCESS)

    return RedirectResponse(url="/login", status_code=303)


@router.get("/login")
def login_page(request: Request):
    # return templates.TemplateResponse(
    #     request=request,
    #     name="login.html",
    #     context={
    #         "title": "User Login",
    #         "flash": get_flash(request),
    #     },
    # )

    return render(
        request=request,
        template="login.html",
        title="Login",
    )


@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = user_service.authenticate_user(
        db=db,
        email=email,
        password=password,
    )

    if user is None:
        return render(
            request=request,
            template="login.html",
            title="Login",
            error="Invalid email or password.",
        )

    request.session["user_id"] = user.id

    set_flash(request, f"Welcome back, {user.username}!", FlashCategory.SUCCESS)
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.pop("user_id", None)

    set_flash(request, "Logged out successfully.", FlashCategory.SUCCESS)
    return RedirectResponse(url="/login", status_code=303)
