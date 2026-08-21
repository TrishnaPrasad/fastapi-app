from fastapi import Depends, Request, Response
from fastapi.responses import RedirectResponse
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import Depends
from app.core.exceptions import LoginRequiredException
from app.core.flash import set_flash

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

from app.services.refresh_token_service import RefreshTokenService

refresh_token_service = RefreshTokenService()

# def get_current_user(request: Request, db: Session = Depends(get_db)):
#     user_id = request.session.get("user_id")

#     if user_id is None:
#         return None

#     return db.query(User).filter(User.id == user_id).first()


def get_current_user(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    access_token = request.cookies.get("access_token")

    if not access_token:
        return None

    try:
        payload = decode_token(access_token)

        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")

        if not user_id:
            return None

    except jwt.ExpiredSignatureError:

        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            return None

        try:
            result = refresh_token_service.rotate_refresh_token(
                db=db,
                refresh_token=refresh_token,
            )

        except jwt.PyJWTError:
            return None

        if result is None:
            return None

        (
            access_token,
            new_refresh_token,
            _,
        ) = result

        # Replace expired access token.
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=5 * 60,
        )

        # Replace rotated refresh token.
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )

        new_payload = decode_token(access_token)
        user_id = new_payload.get("sub")

    except jwt.PyJWTError:
        return None

    return db.query(User).filter(User.id == int(user_id)).first()


def login_required(
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise LoginRequiredException()

        # raise HTTPException(status_code=401, detail="Please login first.")
        # set_flash(request, "Please login first.", FlashCategory.WARNING)

        # set_flash(
        #     request,
        #     "Please login first.",
        #     FlashCategory.WARNING,
        # )

        # raise LoginRequiredException()

        # return RedirectResponse(
        #     url="/login",
        #     status_code=303,
        # )

    return current_user
