from fastapi import Request
from fastapi.responses import RedirectResponse

from app.core.constants import FlashCategory
from app.core.flash import set_flash
from app.core.exceptions import LoginRequiredException


async def login_required_exception_handler(
    request: Request,
    exc: LoginRequiredException,
):
    set_flash(request, "Please login first.", FlashCategory.WARNING)

    return RedirectResponse(
        url="/login",
        status_code=303,
    )
