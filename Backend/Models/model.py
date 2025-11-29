from datetime import datetime, date
import json
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DECIMAL,
    Boolean,
    Enum,
    DateTime,
    Date,
    JSON
)
from sqlalchemy.orm import relationship
from Backend.config import Base


# ---------------- ROLES ----------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role_rel")


# ---------------- USERS ----------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    user_name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)

    otp = Column(Integer, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)

    address = Column(JSON)
    # latitude = Column(DECIMAL(9, 6))
    # longitude = Column(DECIMAL(9, 6))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Boolean, default=True)

    # Relationships
    role_rel = relationship("Role", back_populates="users")
    customer_rel = relationship("Customer", back_populates="user", uselist=False)
    supplier = relationship("Supplier", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="customer")
    deliveries = relationship("Delivery", back_populates="delivery_person")
    payments = relationship("Payment", back_populates="paid_by_user")
    inventory_logs = relationship("InventoryLog", back_populates="created_by_user")


# ---------------- CUSTOMERS ----------------
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    user_name = Column(String(100), nullable=False)
    phone = Column(String(15))
    address = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="customer_rel")


# ---------------- SUPPLIERS ----------------
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    Supplier_name = Column(String(100))
    contact = Column(String(15))
    address = Column(JSON)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="supplier")
    products = relationship("Product", back_populates="supplier")


# ---------------- CATEGORIES ----------------
class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Boolean, default=True)

    products = relationship("Product", back_populates="category")


# ---------------- PRODUCTS ----------------
class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    unit = Column(String(50))
    stock = Column(Integer)

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    category_id = Column(Integer, ForeignKey("categories.category_id"))

    image_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Boolean, default=True)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    orders = relationship("Order", back_populates="product")
    inventory_logs = relationship("InventoryLog", back_populates="product")


# ---------------- ORDERS ----------------
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("users.user_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))

    unit = Column(String(50))
    total_amount = Column(DECIMAL(10, 2))

    status = Column(
        Enum(
            "Pending",
            "Processing",
            "Out for Delivery",
            "Delivered",
            "Cancelled",
            "Subscribed",
        ),
        default="Pending",
    )
    payment_status = Column(Enum("Pending", "Paid", "Failed"), default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order", uselist=False)
    payment = relationship("Payment", back_populates="order", uselist=False)


# ---------------- DELIVERIES ----------------
class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    delivery_person_id = Column(Integer, ForeignKey("users.user_id"))

    status = Column(
        Enum("Pending", "Picked Up", "Delivered", "Cancelled"), default="Pending"
    )
    delivered_at = Column(DateTime)
    remarks = Column(Text)

    order = relationship("Order", back_populates="delivery")
    delivery_person = relationship("User", back_populates="deliveries")


# ---------------- PAYMENTS ----------------
class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    paid_by_user_id = Column(Integer, ForeignKey("users.user_id"))

    payment_method = Column(Enum("Cash", "Card", "UPI", "Wallet"))
    amount = Column(DECIMAL(10, 2))
    transaction_id = Column(String(100))
    payment_date = Column(DateTime, default=datetime.utcnow)

    status = Column(Enum("Success", "Failed", "Pending"), default="Pending")

    paid_user_name = Column(String(100))
    paid_user_email = Column(String(100))
    paid_user_phone = Column(String(15))

    order = relationship("Order", back_populates="payment")
    paid_by_user = relationship("User", back_populates="payments")


# ---------------- INVENTORY LOGS ----------------
class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    change_type = Column(Enum("Added", "Removed", "Sold", "Returned"))
    quantity = Column(Integer)

    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory_logs")
    created_by_user = relationship("User", back_populates="inventory_logs")


# ---------------- SUBSCRIPTIONS ----------------
class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    user_name = Column(String(100))
    product_name = Column(String(100))
    address = Column(JSON)
    quantity_liters = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

    status = Column(Enum("Active", "Inactive", "Cancelled"), default="Active")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# json for address
