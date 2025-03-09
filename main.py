from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.auth import router
from fastapi.middleware.cors import CORSMiddleware
from routes.user import  user_router as user
from routes.product import product_router as product
from routes.order import order_router as orders
from routes.admin import admin_router as admin
from routes.home import home_router as home
from routes.subscription import subscription_router as subscription

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.mount("/upload_image", StaticFiles(directory="uploads_image"), name="upload_image")

app.include_router(user,prefix="/user")
app.include_router(product)
app.include_router(router,prefix="/auth")
app.include_router(orders)
app.include_router(admin)
app.include_router(home)
app.include_router(subscription)

@app.get("/")
async def start():
    return {"message": "Hello User..!"}
