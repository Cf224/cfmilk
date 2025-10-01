from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
import shutil

home_router = APIRouter()

UPLOAD_DIR = "uploads_image"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory database for offers
offers_db = []

@home_router.post("/upload/")
async def upload_offer(file: UploadFile = File(...), offer: str = Form("")):
    """Upload an image with an offer description."""
   
    file_name = str(file.filename)
    file_path = os.path.join(UPLOAD_DIR, file_name)


    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


   
    offer_data = {
        "filename": file_name,
        "offer": offer,
        "url": f"/uploads_images/{file_name}"
    }
    offers_db.append(offer_data)

    return JSONResponse(content={"message": "Upload successful", "data": offer_data})


@home_router.get("/offers/")
async def list_offers():
    """List all uploaded images with their offers."""
    return JSONResponse(content={"offers": offers_db})