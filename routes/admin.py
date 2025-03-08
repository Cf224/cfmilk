from fastapi import APIRouter, HTTPException
from config.config import category_collection, product_collection, order_collection, order_history_collection
from models.model import Category, Product, Order
from datetime import datetime

admin_router = APIRouter()


def get_next_id(collection, id_field):
    last_entry = collection.find_one({}, sort=[(id_field, -1)])
    return last_entry[id_field] + 1 if last_entry else 1




@admin_router.post("/admin/category/add")
def add_category(category: Category):
    existing_category = category_collection.find_one({"name": category.name})

    if existing_category:
        # Update description and measurement fields
        update_data = {
            "description": category.description,
            "measurement": category.measurement
        }
        
        category_collection.update_one(
            {"name": category.name},
            {"$set": update_data}
        )
        return {
            "message": "Category already exists, details updated",
            "category_id": existing_category["category_id"]
        }

    next_category_id = get_next_id(category_collection, "category_id")

    category_data = category.dict()
    category_data["category_id"] = next_category_id 

    category_collection.insert_one(category_data)
    return {"message": "Category added successfully", "category_id": next_category_id}

    existing_category = category_collection.find_one({"name": category.name})

    if existing_category:
        # Update the description and measurement if the category exists
        update_data = {"description": category.description}
        if category.measurement:
            update_data["measurement"] = category.measurement
        
        category_collection.update_one(
            {"name": category.name},
            {"$set": update_data}
        )
        return {
            "message": "Category already exists, details updated",
            "category_id": existing_category["category_id"]
        }

    next_category_id = get_next_id(category_collection, "category_id")

    category_data = category.dict()
    category_data["category_id"] = next_category_id  # Assign integer category_id

    category_collection.insert_one(category_data)
    return {"message": "Category added successfully", "category_id": next_category_id}

@admin_router.get("/admin/categories")
def get_all_categories():
    categories = list(category_collection.find({}, {"_id": 0}))
    
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")
    
    return {"categories": categories}


@admin_router.delete("/admin/category/delete/{name}")
def delete_category(name: str):
    result = category_collection.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}



@admin_router.post("/admin/product/add")
def add_product(product: Product):
    if product_collection.find_one({"name": product.name}):
        raise HTTPException(status_code=400, detail="Product already exists")
    
    product_collection.insert_one(product.dict())
    return {"message": "Product added successfully"}



@admin_router.get("/admin/products")
def get_all_products():
    return list(product_collection.find({}, {"_id": 0}))



@admin_router.post("/admin/orders/insert")
def insert_all_orders(orders: list[Order]):
    inserted_orders = []
    for order in orders:
        if order_collection.find_one({"order_id": order.order_id}):
            continue

        order_data = order.dict()
        order_data["order_date"] = datetime.utcnow()
        order_data["status"] = "pending"
        order_collection.insert_one(order_data)
        order_history_collection.insert_one(order_data)
        inserted_orders.append(order.order_id)

    if not inserted_orders:
        raise HTTPException(status_code=400, detail="No new orders inserted")
    return {"message": "Orders inserted successfully", "orders": inserted_orders}



@admin_router.get("/admin/orders")
def get_all_orders():
    orders = list(order_collection.find({}, {"_id": 0}))
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return {"orders": orders}


@admin_router.delete("/admin/orders/delete/{order_id}")
def delete_order(order_id: str):
    result = order_collection.delete_one({"order_id": order_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": f"Order '{order_id}' deleted successfully"}
