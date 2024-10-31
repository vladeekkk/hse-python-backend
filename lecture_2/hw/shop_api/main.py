from fastapi import (
    FastAPI,
    status,
    Response,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from typing import Dict, List
from .schemas import Item, ItemCreate, Cart, CartItem, ItemBase, ItemUpdate
from .exceptions import ExceptionManager
from prometheus_fastapi_instrumentator import Instrumentator
import string
import random


app = FastAPI(title="Shop API")
Instrumentator().instrument(app).expose(app)

# in memory storage
items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}

item_id_counter = 0
cart_id_counter = 0

exception_manager = ExceptionManager()

def calculate_cart(cart: Cart):
    cart_price = 0
    for cart_item in cart.items:
        item = items_db.get(cart_item.id)
        if item:
            cart_item.available = True
            cart_item.name = item.name
            cart_price += item.price * cart_item.quantity
        else:
            cart_item.available = False
    cart.price = cart_price

    return cart


@app.post("/item", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, response: Response):
    global item_id_counter
    new_item = Item(id=item_id_counter, name=item.name, price=item.price)
    items_db[item_id_counter] = new_item
    response.headers["location"] = f"/item/{new_item.id}"
    item_id_counter += 1
    return new_item


@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    item = items_db.get(id)
    if not item or item.deleted:
        exception_manager.raise_not_found(detail="Item not found in database")
    return item


@app.put("/item/{id}")
def change_item(id: int, new_item: ItemBase):
    item = items_db.get(id)
    if not item or item.deleted:
        exception_manager.raise_not_found(detail="Item not found in database")
    item.name = new_item.name
    item.price = new_item.price
    return item


@app.patch("/item/{id}")
def update_item(id: int, item_update: ItemUpdate):
    item = items_db.get(id)
    if item.deleted:
        exception_manager.raise_not_modified(detail="Attempt to update unaccesible field")
    if "deleted" in item_update:
        exception_manager.raise_unprocessable_entity(detail="Attempt to update unaccesible field")
    if "name" in item_update:
        item.name = item_update.name
    if "price" in item_update:
        item.price = item_update.price
    return item


@app.delete("/item/{id}")
def delete_item(id: int):
    item = items_db.get(id)
    if item is None or item.deleted:
        return {"msg": "Item already removed"}
    item.deleted = True
    return {"msg": "Item removed"}


@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart(response: Response):
    global cart_id_counter
    new_cart = Cart(id=cart_id_counter)
    carts_db[cart_id_counter] = new_cart
    response.headers["location"] = f"/cart/{new_cart.id}"
    cart_id_counter += 1
    return {"id": new_cart.id}


@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    cart = carts_db.get(id)
    if cart is None:
        exception_manager.raise_not_found(detail="Cart not found")
    cart = calculate_cart(cart)
    return cart


@app.get("/cart")
def get_list_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float = Query(None, ge=0.0),
    max_price: float = Query(None, ge=0.0),
    min_quantity: int = Query(None, ge=0),
    max_quantity: int = Query(None, ge=0),
):
    filtered_carts = []
    carts = list(carts_db.values())
    for cart in carts:
        cart = calculate_cart(cart)
        items_quantity = sum([item.quantity for item in cart.items])
        if min_price is not None and cart.price < min_price:
            continue
        if max_price is not None and cart.price > max_price:
            continue
        if min_quantity is not None and items_quantity < min_quantity:
            continue
        if max_quantity is not None and items_quantity > max_quantity:
            continue
        filtered_carts.append(cart)

    return filtered_carts[offset : offset + limit]


@app.get("/item")
def get_list_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float = Query(None, ge=0.0),
    max_price: float = Query(None, ge=0.0),
    show_deleted: bool = Query(False),
):
    filtered_items = []

    items = list(items_db.values())

    for item in items:
        if min_price is not None and item.price < min_price:
            continue
        if max_price is not None and item.price > max_price:
            continue
        if not show_deleted and item.deleted:
            continue
        filtered_items.append(item)
    #    print(filtered_items)
    return filtered_items[offset : offset + limit]


@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_db.get(cart_id)
    if cart is None:
        exception_manager.raise_not_found(detail="Cart not found")

    item = items_db.get(item_id)
    if item is None or item.deleted:
        exception_manager.raise_not_found(detail="Item not found")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart_item = CartItem(
            id=item_id,
            name=item.name,
            quantity=1,
            available=not item.deleted,
        )
        cart.items.append(cart_item)

    return cart


chat_rooms: Dict[str, List[WebSocket]] = {}


def name_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


@app.websocket("/chat/{chat_name}")
async def webscocket_endpoint(websocket: WebSocket, chat_name: str):
    await websocket.accept()

    if chat_name not in chat_rooms:
        chat_rooms[chat_name] = []

    chat_rooms[chat_name].append(websocket)

    user_name = name_generator()

    try:
        while True:
            message = await websocket.receive_text()
            for user_connection in chat_rooms[chat_name]:
                await user_connection.send_text(f"{user_name} :: {message}")
    except WebSocketDisconnect:
        chat_rooms[chat_name].remove(websocket)
        if len(chat_rooms[chat_name]) == 0:
            del chat_rooms[chat_name]