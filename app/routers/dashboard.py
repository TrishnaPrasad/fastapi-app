from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.core.flash import set_flash, get_flash

from app.dependencies.auth import login_required
from app.models.user import User

from app.core.template import render

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request, current_user: User = Depends(login_required)):
    return render(
        request=request,
        template="dashboard.html",
        title="Dashboard",
        current_user=current_user,
    )

    # return templates.TemplateResponse(
    #     request=request,
    #     name="dashboard.html",
    #     context={
    #         "title": "Dashboard",
    #         "current_user": current_user,
    #         "flash": get_flash(request),
    #     },
    # )
