from fastapi import APIRouter, HTTPException
from config.config import product_collection
from models.model import Product

product_router = APIRouter()

# Add Product
@product_router.post("/add")
def add_product(product: Product):
    if product_collection.find_one({"product_id": product.name}):
        raise HTTPException(status_code=400, detail="Product ID already exists")
    product_collection.insert_one(product.dict())
    return {"message": "Product added successfully"}


@product_router.get("/products")
def get_all_products():
    return list(product_collection.find({}, {"_id": 0}))


@product_router.put("/update/{product_id}")
def update_product(product_id: str, product: Product):
    result = product_collection.update_one({"product_id": product_id}, {"$set": product.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}


@product_router.delete("/delete/{product_id}")
def delete_product(product_id: str):
    result = product_collection.delete_one({"product_id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}
