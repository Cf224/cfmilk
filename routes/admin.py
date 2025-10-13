from fastapi import APIRouter, HTTPException
from config.config import category_collection, product_collection, order_collection
from models.model import Category, CategoryUpdate, Product, ProductUpdate


admin_router = APIRouter()


def get_next_id(collection, id_field):
    last_entry = collection.find_one({}, sort=[(id_field, -1)])
    return last_entry[id_field] + 1 if last_entry else 1


@admin_router.post("/admin/category/add")
def add_category(category: Category):
    existing_category = category_collection.find_one({"name": category.name})

    if existing_category:
        raise HTTPException(status_code=400,detail="category already exists")


    next_category_id = get_next_id(category_collection, "id")

    category_data = category.dict()
    category_data["id"] = next_category_id 

    category_collection.insert_one(category_data)
    return {"message": "Category added successfully", "id": next_category_id}

@admin_router.patch("/admin/category/update/{id}")
def update_category(id: int, category: CategoryUpdate):
    existing_category = category_collection.find_one({"id": int(id)})  

    if not existing_category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = {}
    if category.name:
        update_data["name"] = category.name
    if category.description:
        update_data["description"] = category.description
    if category.measurement:
        update_data["measurement"] = category.measurement

    if update_data:
        category_collection.update_one({"id": int(id)}, {"$set": update_data})  
        return {"message": "Category updated successfully", "id": id}
    
    return {"message": "No changes made"}

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
    existing_product = product_collection.find_one({"name" : product.name})
    
    if existing_product:
        raise HTTPException(status_code=400,detail="Product already exist")
        
    next_product_id = get_next_id(product_collection,"id")
    product_data = product.dict()
    product_data["id"] = next_product_id
    
    
        
    product_collection.insert_one(product_data)
    return {
        "message": "Product added successfully",
        "id" : next_product_id,
        "stock":product_data["stock"]
    }

@admin_router.patch("/admin/product/{id}")
def update_products(id:int,product:ProductUpdate):
    existing_product = product_collection.find_one({"id":int(id)})
    
    if not existing_product:
        raise HTTPException(status_code=404,detail="Product Not Found")
    
    update_data = {}
    
    if product.name:
        update_data["name"] = product.name
    if product.category_name:
        update_data["category_name"] = product.category_name
    if product.price:
        update_data["price"] = product.price
    if product.stock:
        update_data["stock"] = product.stock
    if product.description:
        update_data["description"] = product.description                     
    
    if update_data:
        product_collection.update_one({"id": int(id)}, {"$set": update_data})  
        return {"message": "Product updated successfully", "id": id}
    
    return {"message": "No changes made"}    
        
        

    
@admin_router.get("/admin/products")
def get_all_products():
    return list(product_collection.find({}, {"_id": 0}))



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
