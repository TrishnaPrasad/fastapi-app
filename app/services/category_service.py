from sqlalchemy.orm import Session

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:

    def __init__(self):
        self.category_repository = CategoryRepository()

    def create_category(self, db: Session, category: CategoryCreate):

        existing_category = self.category_repository.get_category_by_name(
            db,
            category.name,
        )

        if existing_category:
            return None

        return self.category_repository.create_category(
            db,
            category,
        )

    def get_all_categories(self, db: Session):
        return self.category_repository.get_all_categories(db)

    def get_category_by_id(self, db: Session, category_id: int):
        return self.category_repository.get_active_category_by_id(
            db,
            category_id,
        )

    def update_category(
        self,
        db: Session,
        category_id: int,
        category: CategoryUpdate,
    ):
        db_category = self.category_repository.get_active_category_by_id(
            db,
            category_id,
        )

        if db_category is None:
            return None

        existing_category = self.category_repository.get_category_by_name(
            db,
            category.name,
        )

        if existing_category and existing_category.id != category_id:
            return False

        return self.category_repository.update_category(
            db,
            db_category,
            category,
        )

    def delete_category(self, db: Session, category_id: int):

        db_category = self.category_repository.get_active_category_by_id(
            db,
            category_id,
        )

        if db_category is None:
            return None

        if self.category_repository.has_active_products(
            db,
            category_id,
        ):
            return False

        self.category_repository.delete_category(
            db,
            db_category,
        )

        return True
