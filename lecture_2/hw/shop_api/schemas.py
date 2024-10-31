from pydantic import BaseModel
from typing import List
from typing import Optional


class ItemBase(BaseModel):
    name: str
    price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = {
        "extra": "forbid"
    }


class Item(ItemBase):
    id: int
    deleted: bool = False


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: List[CartItem] = []
    price: float = 0.0