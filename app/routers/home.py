from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.flash import get_flash

from app.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "title": "Inventory Management System",
            "current_user": current_user,
            "flash": get_flash(request),
        },
    )
