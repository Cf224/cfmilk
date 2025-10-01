from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from config.config import subscription_collection
from routes.auth import get_current_user

subscription_router = APIRouter()


PLANS = {"monthly": 30, "quarterly": 90, "yearly": 365}


@subscription_router.post("/subscribe")
def subscribe(plan: str, current_user: dict = Depends(get_current_user)):
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")

    user_id = current_user.get("user_id")
    username = current_user.get("full_name")

    existing_subscription = subscription_collection.find_one({"user_id": user_id})

    if existing_subscription:
        if existing_subscription["expiry_date"] >= datetime.utcnow():
            raise HTTPException(status_code=400, detail="User already subscribed")
        else:
            subscription_collection.delete_one({"user_id": user_id})

    expiry_date = datetime.utcnow() + timedelta(days=PLANS[plan])

    subscription_data = {
        "user_id": user_id,
        "username": username,
        "plan": plan,
        "start_date": datetime.utcnow(),
        "expiry_date": expiry_date,
        "status": "active",
    }
    subscription_collection.insert_one(subscription_data)

    return {
        "message": f"Subscribed to {plan} plan successfully",
        "user_id": user_id,
        "username": username,
        "expiry_date": expiry_date.isoformat(),  # JSON safe
    }


@subscription_router.get("/subscription-status")
def check_subscription(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    subscription = subscription_collection.find_one({"user_id": user_id}, {"_id": 0})

    if not subscription:
        return {"status": "not subscribed"}

    if subscription["expiry_date"] < datetime.utcnow():
        subscription_collection.update_one(
            {"user_id": user_id}, {"$set": {"status": "expired"}}
        )
        return {"status": "expired"}

    subscription["expiry_date"] = subscription["expiry_date"].isoformat()
    subscription["start_date"] = subscription["start_date"].isoformat()
    return subscription


@subscription_router.delete("/unsubscribe")
def unsubscribe(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    result = subscription_collection.delete_one({"user_id": user_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return {"message": "Unsubscribed successfully"}


@subscription_router.get("/admin/all-subscriptions")
def get_all_subscriptions(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    subscriptions = list(subscription_collection.find({}, {"_id": 0}))
    if not subscriptions:
        raise HTTPException(status_code=404, detail="No subscriptions found")

    for sub in subscriptions:
        if "expiry_date" in sub:
            sub["expiry_date"] = sub["expiry_date"].isoformat()
        if "start_date" in sub:
            sub["start_date"] = sub["start_date"].isoformat()

    return {"subscriptions": subscriptions}
