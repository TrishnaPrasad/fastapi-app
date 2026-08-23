from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse

# from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.constants import FlashCategory
from app.core.flash import set_flash, get_flash

from app.database import get_db
from app.schemas.user import UserCreate
from app.services.user_service import UserService
import app.config as settings

from app.core.template import render

from app.core.security import create_access_token
from app.services.refresh_token_service import RefreshTokenService

refresh_token_service = RefreshTokenService()

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

    access_token = create_access_token(user.id)

    refresh_token, refresh_token_record = refresh_token_service.create_refresh_token(
        db=db,
        user_id=user.id,
    )

    print("LOGIN USER:", user.id)
    print("ACCESS TOKEN CREATED")
    print("REFRESH TOKEN CREATED")
    print("REFRESH TOKEN DB ID:", refresh_token_record.id)

    request.session["user_id"] = user.id

    set_flash(request, f"Welcome back, {user.username}!", FlashCategory.SUCCESS)

    response = RedirectResponse(
        url="/dashboard",
        status_code=303,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return response


# @router.get("/logout")
# def logout(request: Request):
# request.session.pop("user_id", None)

# set_flash(request, "Logged out successfully.", FlashCategory.SUCCESS)
# return RedirectResponse(url="/login", status_code=303)


@router.get("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        refresh_token_service.revoke_by_token(
            db=db,
            token=refresh_token,
        )

    set_flash(
        request,
        "Logged out successfully.",
        FlashCategory.SUCCESS,
    )

    response = RedirectResponse(
        url="/login",
        status_code=303,
    )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response
