from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.constants import FlashCategory
from app.core.template import render
from app.database import get_db
from app.services.category_service import CategoryService
from app.dependencies.auth import login_required
from app.models.user import User

from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.flash import set_flash
from fastapi.responses import RedirectResponse

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

category_service = CategoryService()


@router.get("/categories")
def category_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    categories = category_service.get_all_categories(db)

    return render(
        request=request,
        template="categories/list.html",
        title="Categories",
        categories=categories,
        current_user=current_user,
    )


@router.get("/categories/create")
def create_category_page(
    request: Request,
    current_user: User = Depends(login_required),
):
    return render(
        request=request,
        template="categories/create.html",
        context={
            "title": "Create Category",
        },
        current_user=current_user,
    )


@router.post("/categories/create")
def create_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    category = CategoryCreate(
        name=name,
        description=description,
    )

    created_category = category_service.create_category(
        db,
        category,
    )

    if created_category is None:
        return render(
            request=request,
            template="categories/create.html",
            title="Create Category",
            current_user=current_user,
            error="A category with this name already exists.",
            form_data={
                "name": name,
                "description": description,
            },
        )

    set_flash(
        request,
        "Category created successfully.",
        FlashCategory.SUCCESS,
    )

    return RedirectResponse(
        url="/categories",
        status_code=303,
    )


@router.get("/categories/{category_id}/edit")
def edit_category_page(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    category = category_service.get_category_by_id(db, category_id)

    if category is None:
        set_flash(
            request,
            "Category not found.",
            FlashCategory.ERROR,
        )

        return RedirectResponse(
            url="/categories",
            status_code=303,
        )

    return render(
        request=request,
        template="categories/edit.html",
        title="Edit Category",
        category=category,
        current_user=current_user,
    )


@router.post("/categories/{category_id}/edit")
def edit_category(
    request: Request,
    category_id: int,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    category = category_service.update_category(
        db=db,
        category_id=category_id,
        category=CategoryUpdate(
            name=name,
            description=description,
        ),
    )

    if category is None:
        set_flash(
            request,
            "Category not found.",
            FlashCategory.ERROR,
        )

        return RedirectResponse(
            url="/categories",
            status_code=303,
        )

    if category is False:

        existing_category = category_service.get_category_by_id(db, category_id)

        return render(
            request=request,
            template="categories/edit.html",
            title="Edit Category",
            category=existing_category,
            current_user=current_user,
            error="A category with this name already exists.",
            form_data={
                "name": name,
                "description": description,
            },
        )

    set_flash(
        request,
        "Category updated successfully.",
        FlashCategory.SUCCESS,
    )

    return RedirectResponse(
        url="/categories",
        status_code=303,
    )


@router.get("/categories/{category_id}/delete")
def delete_category_page(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    category = category_service.get_active_category_by_id(
        db,
        category_id,
    )

    if category is None:
        set_flash(
            request,
            "Category not found.",
            FlashCategory.ERROR,
        )

        return RedirectResponse(
            url="/categories",
            status_code=303,
        )

    return render(
        request=request,
        template="categories/delete.html",
        title="Delete Category",
        category=category,
        current_user=current_user,
    )


@router.post("/categories/{category_id}/delete")
def delete_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    deleted_category = category_service.delete_category(
        db=db,
        category_id=category_id,
    )

    if deleted_category is None:
        set_flash(
            request,
            "Category not found.",
            FlashCategory.ERROR,
        )
    elif deleted_category is False:
        set_flash(
            request,
            "Cannot delete category because it has products assigned to it.",
            FlashCategory.ERROR,
        )

    else:
        set_flash(
            request,
            "Category deleted successfully.",
            FlashCategory.SUCCESS,
        )

    return RedirectResponse(
        url="/categories",
        status_code=303,
    )
