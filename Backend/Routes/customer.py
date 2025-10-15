from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from Backend.Models.model import CustomerUpdate, User as UserModel, Customer
from Backend.config import SessionLocal
from Backend.Routes.auth import get_current_user

customer_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@customer_router.put("/customer/register", tags=["Customer"])
async def customer_register(
    cust_upt: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    user = db.query(UserModel).filter(UserModel.user_id == current_user.user_id).first()
    customer = (
        db.query(Customer).filter(Customer.user_id == current_user.user_id).first()
    )

    if not user or not customer:
        raise HTTPException(status_code=404, detail="User or Customer not found")

    update_data = cust_upt.dict(exclude_unset=True)

    user_columns = {col.name for col in UserModel.__table__.columns}
    customer_columns = {col.name for col in Customer.__table__.columns}

    updated_user_fields, updated_customer_fields = {}, {}

    for key, value in update_data.items():
        if key in user_columns:
            setattr(user, key, value)
            updated_user_fields[key] = value
        if key in customer_columns:
            setattr(customer, key, value)
            updated_customer_fields[key] = value

    # Update timestamps
    if hasattr(user, "updated_at"):
        user.updated_at = datetime.utcnow()  # type:ignore
    if hasattr(customer, "updated_at"):
        customer.updated_at = datetime.utcnow()  # type:ignore

    db.commit()
    db.refresh(user)
    db.refresh(customer)

    return {
        "message": "Customer and user profile updated successfully",
        "updated_customer": updated_customer_fields,
    }
