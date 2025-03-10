from pydantic import BaseModel, Field, EmailStr, constr
from typing import  Optional,Dict,Any
from datetime import datetime




class User(BaseModel):
    user_id: constr(pattern="^user\d+$") = Field(...) #type:ignore
    username: str = Field(..., min_length=3, max_length=50)
    phone_number: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Product(BaseModel):
    name : str
    category_name: str
    price: float
    stock: int
    description: Dict[str,Any]

class ProductUpdate(BaseModel):
    name : Optional[str] = None
    category_name:Optional[str]=None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[Dict[str,Any]] = None


class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float



class Order(BaseModel):
    order_id: str
    product_id: str
    quantity: int
    category: str
    total_price: float
    status: str = Field(default="pending")
    order_date: datetime = Field(default_factory=datetime.utcnow)




class Subscription(BaseModel):
    user_id: str
    product_id: str
    quantity: int
    frequency: str 
    next_delivery_date: datetime


class EmailRequest(BaseModel):
    email: EmailStr


class OtpVerification(BaseModel):
    email: EmailStr
    otp: int

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None



class RegisterForm(BaseModel):
    full_name: str
    phone_number: str
    email: str
    age:int
    gender:str

class OrderStatus(BaseModel):
    status: str


class Category(BaseModel):
    name: str 
    description: Dict[str, Any]
    measurement : str

class CategoryUpdate(BaseModel):
    name: Optional[str] = None 
    description: Optional[Dict[str, Any]] = None
    measurement : Optional[str] = None
 

def create_indexes(db):
    db.users.create_index("phone_number", unique=True)
    db.products.create_index("category")
    db.orders.create_index("user_id")
    db.orders.create_index("order_date")
    db.order_history.create_index("user_id")
    db.subscriptions.create_index("user_id")
    db.users.create_index("otp")
    print("Indexes created successfully")
