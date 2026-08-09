from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:

    def create_product(
        self,
        db: Session,
        product: ProductCreate,
    ):
        db_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
        )

        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        return db_product

    def get_all_products(self, db: Session):
        return db.query(Product).order_by(Product.name).all()

    def get_product_by_id(
        self,
        db: Session,
        product_id: int,
    ):
        return db.query(Product).filter(Product.id == product_id).first()

    def get_active_product_by_id(
        self,
        db: Session,
        product_id: int,
    ):
        return (
            db.query(Product)
            .filter(Product.id == product_id, Product.is_active.is_(True))
            .first()
        )

    def get_product_by_name(
        self,
        db: Session,
        name: str,
    ):
        return db.query(Product).filter(Product.name == name).first()

    def update_product(
        self,
        db: Session,
        db_product: Product,
        product: ProductUpdate,
    ):
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.category_id = product.category_id

        db.commit()
        db.refresh(db_product)

        return db_product

    # def delete_product(
    #     self,
    #     db: Session,
    #     db_product: Product,
    # ):
    #     db.delete(db_product)
    #     db.commit()

    def delete_product(self, db: Session, db_product: Product):
        db_product.is_active = False

        db.commit()
        db.refresh(db_product)

        return db_product
