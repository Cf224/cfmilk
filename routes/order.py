from fastapi import APIRouter, HTTPException, Depends
from config.config import (
    order_collection,
    product_collection,
    user_collection,
    order_history_collection,
)
from models.model import OrderItem, OrderStatus
from datetime import datetime
from uuid import uuid4
from routes.auth import get_current_user
from routes.user import get_live_location

order_router = APIRouter()


@order_router.post("/my-orders/place_order")
def place_order(order: OrderItem, current_user: dict = Depends(get_current_user)):
    product = product_collection.find_one({"name": order.product_name})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if order.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    user = user_collection.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    live_location = get_live_location()
    order_id = f"order_{uuid4().hex[:6]}"
    total_price = order.quantity * product["price"]

    order_data = {
        "order_id": order_id,
        "user_id": str(user["_id"]),
        "product_name": product["name"],
        "category": product["category_name"],
        "quantity": order.quantity,
        "total_price": total_price,
        "status": "pending",
        "order_date": datetime.utcnow(),
        "location": live_location,
    }

    order_collection.insert_one(order_data)
    order_history_collection.insert_one(order_data)

    return {
        "message": "Order placed successfully",
        "order_id": order_id,
        "product_name": product["name"],
        "quantity": order.quantity,
        "total_price": total_price,
        "location": live_location,
    }



@order_router.get("/my-orders")
def get_current_user_orders(
    current_user: dict = Depends(get_current_user), category: str = None):  # type:ignore
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")

    query = {"user_id": user_id}
    if category:
        query["category"] = category

    orders = list(order_collection.find(query, {"_id": 0}))
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")

    return {"orders": orders}


@order_router.put("/my-orders/update/{order_id}")
def update_order_status(
    order_id: str,
    status_data: OrderStatus,
    current_user: dict = Depends(get_current_user),
):
    valid_statuses = {"shipped", "pending", "delivered"}
    if status_data.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}",
        )

    # Find the order
    order = order_collection.find_one(
        {"order_id": order_id, "user_id": current_user["user_id"]}
    )
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found or does not belong to the current user",
        )

    
    order_collection.update_one(
        {"order_id": order_id}, {"$set": {"status": status_data.status}}
    )

    
    if status_data.status == "delivered":
        
        order_collection.delete_one({"order_id": order_id})
        
        order["status"] = "complete"
        order_history_collection.update_one(
            {"order_id": order_id}, {"$set": order}, upsert=True
        )

    return {"message": f"Order status updated to '{status_data.status}' successfully"}


#  Delete Order for Current User
@order_router.delete("/my-orders/delete/{order_id}")
def delete_current_user_order(
    order_id: str, current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")

    # Ensure order belongs to the user
    result = order_collection.delete_one({"order_id": order_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Order not found or does not belong to the current user",
        )

    return {"message": "Order deleted successfully"}
