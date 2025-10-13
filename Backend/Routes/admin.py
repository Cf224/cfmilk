from fastapi import APIRouter, Depends, HTTPException
from Backend.Models.model import (
    User,
    Role,
    Product,
    Category,
    CreateCategoryRequest,
    CreateUserRequest,
    CreateProductRequest,
)
from sqlalchemy.orm import Session
from Backend.config import SessionLocal
from Backend.Routes.auth import get_current_user
from datetime import datetime

admin_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User Api


@admin_router.get("/admin/users", tags=["Admin"])
async def get_all_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    admin_role = current_user.role_rel.name if current_user.role_rel else ""
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add new users")

    all_users = db.query(User).all()

    if not all_users:
        raise HTTPException(status_code=404, detail="Don't have Any users in Database")

    result = []
    for user in all_users:
        role_name = user.role_rel.name if user.role_rel else "unknown"
        result.append(
            {
                "user_id": user.user_id,
                "user_name": user.user_name,
                "phone": user.phone,
                "role_id": user.role_id,
                "role_name": role_name,
                "is_verified": user.is_verified,
                "status": user.status,
            }
        )

    return {"users": result}


@admin_router.get("/admin/users/role/{role_name}", tags=["Admin"])
async def get_users_by_role(
    role_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_role = current_user.role_rel.name if current_user.role_rel else ""
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add new users")

    # Get the role object
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    users = db.query(User).filter(User.role_id == role.id).all()
    if not users:
        return {"users": []}  # return empty list if no users found

    result = []
    for user in users:
        result.append(
            {
                "user_id": user.user_id,
                "user_name": user.user_name,
                "phone": user.phone,
                "role_id": user.role_id,
                "role_name": role.name,
                "is_verified": user.is_verified,
                "status": user.status,
            }
        )

    return {"users": result}


@admin_router.post("/admin/add-user", tags=["Admin"])
async def add_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_role = current_user.role_rel.name if current_user.role_rel else ""
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add new users")

    role = db.query(Role).filter(Role.name == request.role_name).first()
    if not role or request.role_name not in ["supplier", "delivery"]:
        raise HTTPException(status_code=400, detail="Invalid role to add")

    existing_user = db.query(User).filter(User.phone == request.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this phone already exists"
        )

    last_user = db.query(User).order_by(User.id.desc()).first()
    next_id = 1001 if not last_user else int(last_user.user_id[4:]) + 1
    user_id = f"user{next_id}"

    new_user = User(
        user_id=user_id,
        user_name=request.user_name,
        phone=request.phone,
        role_id=role.id,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        status="active",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"{request.role_name.capitalize()} added successfully",
        "user_id": new_user.user_id,
        "user_name": new_user.user_name,
        "phone": new_user.phone,
        "role_name": role.name,
    }


# Product APi


@admin_router.get("/admin/all_Products", tags=["Admin"])
async def get_all_product(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_role = current_user.role_rel.name if current_user.role_rel else ""
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add new users")

    all_Products = db.query(Product).all()

    if not all_Products:
        raise HTTPException(
            status_code=404, detail="Don't have Any Product's in Database"
        )

    result = []

    for product in all_Products:
        # products = product.name.name if product.name else "unknown"
        result.append(
            {
                "Product_id": product.id,
                "Product_name": product.name,
                "Price": product.price,
                "Stock": product.stock,
                "Unit": product.unit,
                "Description": product.description,
            }
        )

    return {"users": result}


@admin_router.post("/admin/add_product",tags=["Admin"])
async def add_product(
    request: CreateProductRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Check admin
    admin_role = current_user.role_rel.name if current_user.role_rel else ""
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add a new product!")

    # Get category object
    category = db.query(Category).filter(Category.name == request.category_name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check duplicate product
    existing_product = db.query(Product).filter(Product.name == request.product_name).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="This product already exists")

    # Generate product_id
    last_product = db.query(Product).order_by(Product.id.desc()).first()
    next_id = 1001 if not last_product else last_product.id + 1
    product_id = f"Product{next_id}"

    # Create product
    new_product = Product(
        product_id=product_id,
        name=request.product_name,
        description=request.description,
        price=request.price,
        unit=request.unit,
        stock=request.stock,
        supplier_id=request.supplier_id,
        category_id=category.id,  
        image_url=request.image_url,
        created_at=datetime.utcnow(),
        status=request.status,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": f"Product '{request.product_name}' added successfully.",
        "category": category.name,
        "price": request.price,
        "unit": request.unit,
        "stock": request.stock,
        "status": request.status
    }

@admin_router.get("/admin/all_Category", tags=["Admin"])
async def all_Category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_role = current_user.role_rel.name if current_user.role_rel else ""
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can See the categories")

    all_category = db.query(Category).all()
    if not all_category:
        raise HTTPException(
            status_code=404, detail="Don't have Any Category in Database"
        )

    result = []

    for category in all_category:
        result.append(
            {
                "category_id": category.category_id,
                "category_name": category.name,
            }
        )

    return {"Category": result}


@admin_router.post("/admin/add_category", tags=["Admin"])
async def add_category(
    request: CreateCategoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    admin_role = current_user.role_rel.name if current_user.role_rel else ""
    if admin_role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add categories")

    existing_category = (
        db.query(Category).filter(Category.name == request.category_name).first()
    )
    if existing_category:
        raise HTTPException(status_code=400, detail="This category already exists")

    last_category = db.query(Category).order_by(Category.id.desc()).first()
    next_id = 1001 if not last_category else int(last_category.category_id[8:]) + 1
    category_id = f"Category{next_id}"

    new_category = Category(
        category_id=category_id,
        name=request.category_name,
        description=request.description,
       
        created_at=datetime.utcnow(),
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {
        "message": f"Category '{request.category_name}' added successfully.",
        "category_id": category_id,
        "status": request.status,
    }
