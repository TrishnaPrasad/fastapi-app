from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:

    def __init__(self):
        self.user_repository = UserRepository()

    def create_user(self, db: Session, user: UserCreate):

        existing_user = self.user_repository.get_user_by_email(db, user.email)

        if existing_user:
            return None

        user.password = hash_password(user.password)
        return self.user_repository.create_user(db, user)

    def authenticate_user(self, db: Session, email: str, password: str):
        # Find user by email
        user = self.user_repository.get_user_by_email(db, email)

        if not user:
            return None

        # Verify password
        if not verify_password(password, user.password):
            return None

        return user
