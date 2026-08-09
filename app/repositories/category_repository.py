from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:

    def create_category(self, db: Session, category: CategoryCreate):
        db_category = Category(
            name=category.name,
            description=category.description,
        )

        db.add(db_category)
        db.commit()
        db.refresh(db_category)

        return db_category

    def get_all_categories(self, db: Session):
        return (
            db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.name)
            .all()
        )

    def get_category_by_id(self, db: Session, category_id: int):
        return db.query(Category).filter(Category.id == category_id).first()

    def get_active_category_by_id(
        self,
        db: Session,
        category_id: int,
    ):
        return (
            db.query(Category)
            .filter(
                Category.id == category_id,
                Category.is_active.is_(True),
            )
            .first()
        )

    def get_category_by_name(self, db: Session, name: str):
        return db.query(Category).filter(Category.name == name).first()

    def update_category(
        self,
        db: Session,
        db_category: Category,
        category: CategoryUpdate,
    ):
        db_category.name = category.name
        db_category.description = category.description

        db.commit()
        db.refresh(db_category)

        return db_category

    # def delete_category(self, db: Session, db_category: Category):
    #     db.delete(db_category)
    #     db.commit()
    def delete_category(self, db: Session, db_category: Category):
        db_category.is_active = False

        db.commit()
        db.refresh(db_category)

        return db_category
