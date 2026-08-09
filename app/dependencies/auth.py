from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import Depends
from app.core.exceptions import LoginRequiredException
from app.core.flash import set_flash

from app.database import get_db
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if user_id is None:
        return None

    return db.query(User).filter(User.id == user_id).first()


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
