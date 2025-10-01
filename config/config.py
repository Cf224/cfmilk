import os
from pymongo.mongo_client import MongoClient
from fastapi_mail import ConnectionConfig


MONGO_URI = "mongodb+srv://praveen03:2024Admin@cluster0.ztr6g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

if not MONGO_URI:
    raise ValueError("Mongo URI is not set in the .env file!")


client = MongoClient(MONGO_URI)
db = client.get_database("myBlogs")


user_collection = db["users"]
product_collection = db["Product"]
order_collection = db["orders"]
order_history_collection = db["History"]
category_collection = db["category_Collection"]
subscription_collection = db["subscriptions_Collection"]


SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Email configuration from environment variables
EMAIL_CONF = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "chinnafarming@gmail.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "hngv plme oktm egmr"),  # type:ignore
    MAIL_FROM=os.getenv("MAIL_FROM", "chinnafarming@gmail.com"),
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


try:
    client = MongoClient(MONGO_URI)
    db = client.get_database("myBlogs")

    user_collection = db["users"]
    product_collection = db["Product"]

    print("Connection successful...!")

except ConnectionError as e:
    print(f"Failed to connect to MongoDB: {e}")
