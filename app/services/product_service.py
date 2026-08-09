from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    def __init__(self):
        self.product_repository = ProductRepository()

    def create_product(
        self,
        db: Session,
        product: ProductCreate,
    ):
        existing_product = self.product_repository.get_product_by_name(
            db,
            product.name,
        )

        if existing_product:
            return None

        return self.product_repository.create_product(
            db,
            product,
        )

    def get_all_products(self, db: Session):
        return self.product_repository.get_all_products(db)

    def get_product_by_id(
        self,
        db: Session,
        product_id: int,
    ):
        return self.product_repository.get_active_product_by_id(
            db,
            product_id,
        )

    def update_product(
        self,
        db: Session,
        product_id: int,
        product: ProductUpdate,
    ):
        db_product = self.product_repository.get_active_product_by_id(
            db,
            product_id,
        )

        if db_product is None:
            return None

        existing_product = self.product_repository.get_product_by_name(
            db,
            product.name,
        )

        if existing_product and existing_product.id != product_id:
            return False

        return self.product_repository.update_product(
            db,
            db_product,
            product,
        )

    def delete_product(
        self,
        db: Session,
        product_id: int,
    ):
        db_product = self.product_repository.get_active_product_by_id(
            db,
            product_id,
        )

        if db_product is None:
            return None

        self.product_repository.delete_product(
            db,
            db_product,
        )

        return True
