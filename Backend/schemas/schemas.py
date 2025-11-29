
from pydantic import BaseModel,Field
from typing import Literal,Optional
from datetime import date

class BaseSchema(BaseModel):
    class Config:
        orm_mode = True

class PhoneRequest(BaseSchema):
    phone: str
    
class OtpVerification(BaseSchema):
    phone: str = Field(min_length=10,max_length=15)
    otp: int

class CreateUserRequest(BaseSchema):
    user_name: str = Field(min_length=3,max_length=50,pattern="^[a-zA-Z]")
    phone: str = Field(min_length=10,max_length=15)
    role_name: str = Literal["customer", "supplier","delivery"] # type: ignore

class CreateCategoryRequest(BaseSchema):
    category_name : str = Field(min_length=3,max_length=50,pattern="^[a-zA-Z]")
    description : str 
    status:bool = True
    
class CreateProductRequest(BaseSchema):
    product_name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    price: float
    unit: str
    stock: int = 0
    category_name: str
    supplier_id: Optional[int] = None
    image_url: Optional[str] = None
    status: bool = True
    
class UpdateProductStockRequest(BaseSchema):
    product_name: str
    new_stock: int


class CustomerUpdate(BaseSchema):
    user_name: Optional[str] = None
    phone : Optional[str] = None
    address: dict | None = None
    

class CustomerResponse(BaseSchema):
    user_name: str
    phone : str 
    address: Optional[str] = None

    
    
class CustomerOrders(BaseSchema):
    name:str
    quantity:int    
    
class Customersubscription(BaseSchema):
    product_name: str
    quantity_liters: float
    start_date: date
    end_date: date

class AllProductResponse(BaseSchema):
    name: str
    description: Optional[str] = None
    price: float
    unit: str
    stock: int
    category_name: str
    image_url: Optional[str] = None
    status: bool