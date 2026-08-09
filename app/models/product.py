from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    description = Column(String(500), nullable=True)

    price = Column(Float, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
    )

    category = relationship(
        "Category",
        back_populates="products",
    )
