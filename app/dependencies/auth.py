import jwt

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import LoginRequiredException
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

# def get_current_user(request: Request, db: Session = Depends(get_db)):
#     user_id = request.session.get("user_id")

#     if user_id is None:
#         return None

#     return db.query(User).filter(User.id == user_id).first()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    access_token = getattr(
        request.state,
        "access_token",
        None,
    )

    if access_token is None:
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
