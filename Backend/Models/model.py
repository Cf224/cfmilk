from datetime import datetime
from typing import Literal,Optional
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DECIMAL, Boolean, Enum, DateTime
)
from sqlalchemy.orm import relationship
from Backend.config import Base
from pydantic import BaseModel,Field


class PhoneRequest(BaseModel):
    phone: str

class OtpVerification(BaseModel):
    phone: str = Field(min_length=10,max_length=15)
    otp: int 

class CreateUserRequest(BaseModel):
    user_name: str = Field(min_length=3,max_length=50,pattern="^[a-zA-Z]")
    phone: str = Field(min_length=10,max_length=15)
    role_name: str = Literal["customer", "supplier","delivery"]

class CreateCategoryRequest(BaseModel):
    category_name : str = Field(min_length=3,max_length=50,pattern="^[a-zA-Z]")
    description : str 
    status: Literal["active", "inactive"] = "active"
    
class CreateProductRequest(BaseModel):
    product_name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    price: float
    unit: str
    stock: int = 0
    category_name: str
    supplier_id: Optional[int] = None
    image_url: Optional[str] = None   
    status: Literal["active", "inactive"] = "active"
    
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    users = relationship("User", back_populates="role_rel")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key linking to Role
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)

    user_id = Column(String(50), unique=True)
    user_name = Column(String(100), nullable=False)
    # role = Column(Enum('admin', 'customer', 'supplier', 'delivery'))
    phone = Column(String(15), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role_rel = relationship("Role", back_populates="users")
    
    otp = Column(Integer, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)

    address = Column(String(255))
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Boolean,default=True)

    # Relationships
    role_rel = relationship("Role", back_populates="users")  
    supplier = relationship("Supplier", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="customer")
    deliveries = relationship("Delivery", back_populates="delivery_person")
    payments = relationship("Payment", back_populates="paid_by_user")
    inventory_logs = relationship("InventoryLog", back_populates="created_by_user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
# ---------- SUPPLIERS ----------
class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    company_name = Column(String(100))
    contact = Column(String(15))
    address = Column(String(255))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="supplier")
    products = relationship("Product", back_populates="supplier")

# ---------- CATEGORIES ----------
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with products
    products = relationship("Product", back_populates="category")
    status = Column(Boolean ,default=True)


# ---------- PRODUCTS ----------
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), unique=True) 
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    unit = Column(String(50))
    stock = Column(Integer, default=0)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    image_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum('active', 'inactive'), default='active')

    category = relationship("Category", back_populates="products")  
    supplier = relationship("Supplier", back_populates="products")
    orders = relationship("Order", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")


# ---------- ORDERS ----------
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    unit = Column(String(50))
    total_amount = Column(DECIMAL(10, 2))
    status = Column(Enum('Pending', 'Processing', 'Out for Delivery', 'Delivered', 'Cancelled'), default='Pending')
    payment_status = Column(Enum('Pending', 'Paid', 'Failed'), default='Pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order", uselist=False)
    payment = relationship("Payment", back_populates="order", uselist=False)

# ---------- DELIVERIES ----------
class Delivery(Base):
    __tablename__ = 'deliveries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    delivery_person_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum('Pending', 'Picked Up', 'Delivered', 'Cancelled'), default='Pending')
    delivered_at = Column(DateTime)
    remarks = Column(Text)

    order = relationship("Order", back_populates="delivery")
    delivery_person = relationship("User", back_populates="deliveries")


# ---------- PAYMENTS ----------
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    paid_by_user_id = Column(Integer, ForeignKey('users.id'))
    payment_method = Column(Enum('Cash', 'Card', 'UPI', 'Wallet'))
    amount = Column(DECIMAL(10, 2))
    transaction_id = Column(String(100))
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('Success', 'Failed', 'Pending'), default='Pending')
    paid_user_name = Column(String(100))
    paid_user_email = Column(String(100))
    paid_user_phone = Column(String(15))

    order = relationship("Order", back_populates="payment")
    paid_by_user = relationship("User", back_populates="payments")


# ---------- INVENTORY LOGS ----------
class InventoryLog(Base):
    __tablename__ = 'inventory_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    change_type = Column(Enum('Added', 'Removed', 'Sold', 'Returned'))
    quantity = Column(Integer)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_logs")
    created_by_user = relationship("User", back_populates="inventory_logs")
