from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    category_id: int


class ProductUpdate(BaseModel):
    name: str
    description: str | None = None
    price: float
    category_id: int
