from fastapi import Request

from app.core.constants import FlashCategory


def set_flash(
    request: Request,
    message: str,
    category: FlashCategory = FlashCategory.SUCCESS,
):
    """
    Add a flash message to the session.
    Supports multiple flash messages.
    """
    flashes = request.session.get("_flash", [])

    flashes.append(
        {
            "message": message,
            "category": category.value,
        }
    )

    request.session["_flash"] = flashes


def get_flash(request: Request):
    """
    Retrieve all flash messages and remove them from the session.
    """
    return request.session.pop("_flash", [])
