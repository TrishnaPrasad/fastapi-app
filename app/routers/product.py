from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import login_required
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.core.constants import FlashCategory
from app.core.flash import set_flash
from app.core.template import render

router = APIRouter()

product_service = ProductService()
category_service = CategoryService()


# ============================================================
# LIST PRODUCTS
# ============================================================


@router.get("/products")
def product_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    products = product_service.get_all_products(db)

    return render(
        request=request,
        template="products/list.html",
        title="Products",
        products=products,
        current_user=current_user,
    )


# ============================================================
# CREATE PRODUCT - GET
# ============================================================


@router.get("/products/create")
def create_product_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    categories = category_service.get_all_categories(db)

    return render(
        request=request,
        template="products/create.html",
        title="Create Product",
        categories=categories,
        current_user=current_user,
    )


# ============================================================
# CREATE PRODUCT - POST
# ============================================================


@router.post("/products/create")
def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    product = ProductCreate(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
    )

    created_product = product_service.create_product(
        db,
        product,
    )

    if created_product is None:
        categories = category_service.get_all_categories(db)

        return render(
            request=request,
            template="products/create.html",
            title="Create Product",
            categories=categories,
            current_user=current_user,
            error="A product with this name already exists.",
            form_data={
                "name": name,
                "description": description,
                "price": price,
                "category_id": category_id,
            },
        )

    set_flash(
        request,
        "Product created successfully.",
        FlashCategory.SUCCESS,
    )

    return RedirectResponse(
        url="/products",
        status_code=303,
    )


# ============================================================
# EDIT PRODUCT - GET
# ============================================================


@router.get("/products/{product_id}/edit")
def edit_product_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    product = product_service.get_product_by_id(
        db,
        product_id,
    )

    if product is None:
        set_flash(
            request,
            "Product not found.",
            FlashCategory.ERROR,
        )

        return RedirectResponse(
            url="/products",
            status_code=303,
        )

    categories = category_service.get_all_categories(db)

    return render(
        request=request,
        template="products/edit.html",
        title="Edit Product",
        product=product,
        categories=categories,
        current_user=current_user,
    )


# ============================================================
# EDIT PRODUCT - POST
# ============================================================


@router.post("/products/{product_id}/edit")
def edit_product(
    request: Request,
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    product = ProductUpdate(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
    )

    updated_product = product_service.update_product(
        db,
        product_id,
        product,
    )

    # Product doesn't exist
    if updated_product is None:
        set_flash(
            request,
            "Product not found.",
            FlashCategory.ERROR,
        )

        return RedirectResponse(
            url="/products",
            status_code=303,
        )

    # Duplicate product name
    if updated_product is False:
        categories = category_service.get_all_categories(db)

        return render(
            request=request,
            template="products/edit.html",
            title="Edit Product",
            categories=categories,
            current_user=current_user,
            error="A product with this name already exists.",
            form_data={
                "name": name,
                "description": description,
                "price": price,
                "category_id": category_id,
            },
            product=product_service.get_product_by_id(
                db,
                product_id,
            ),
        )

    set_flash(
        request,
        "Product updated successfully.",
        FlashCategory.SUCCESS,
    )

    return RedirectResponse(
        url="/products",
        status_code=303,
    )


# ============================================================
# Get Delete PRODUCT
# ============================================================


@router.get("/products/{product_id}/delete")
def delete_product_page(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    product = product_service.get_product_by_id(
        db,
        product_id,
    )

    if product is None or not product.is_active:
        set_flash(
            request,
            "Product not found.",
            FlashCategory.ERROR,
        )

        return RedirectResponse(
            url="/products",
            status_code=303,
        )

    return render(
        request=request,
        template="products/delete.html",
        title="Delete Product",
        product=product,
        current_user=current_user,
    )


# ============================================================
# DELETE PRODUCT
# ============================================================


@router.post("/products/{product_id}/delete")
def delete_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(login_required),
):
    deleted = product_service.delete_product(
        db,
        product_id,
    )

    if deleted is None:
        set_flash(
            request,
            "Product not found.",
            FlashCategory.ERROR,
        )
    else:
        set_flash(
            request,
            "Product deleted successfully.",
            FlashCategory.SUCCESS,
        )

    return RedirectResponse(
        url="/products",
        status_code=303,
    )
