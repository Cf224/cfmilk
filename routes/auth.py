from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from config.config import user_collection, EMAIL_CONF, SECRET_KEY, ALGORITHM
from fastapi_mail import FastMail, MessageSchema
from datetime import datetime, timedelta
from jose import jwt, JWTError
import random
import re
from models.model import EmailRequest, OtpVerification

router = APIRouter()
fast_mail = FastMail(EMAIL_CONF)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def generate_user_id():
    last_user = user_collection.find_one(
        {"user_id": {"$regex": "^user"}}, sort=[("user_id", -1)]
    )
    if last_user and "user_id" in last_user:
        try:
            last_id = int(last_user["user_id"].replace("user", ""))
            return f"user{last_id + 1}"
        except ValueError:
            return "user1"
    return "user1"


def validate_email(email: str) -> bool:
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    email = decode_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = user_collection.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["sub"] = email
    return user




@router.post("/login")
async def send_otp(request: EmailRequest):
    email = request.email

    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
        )

    user = user_collection.find_one({"email": email})

    if user:
        username = user.get("username", "User")
        role = user.get("role", "user")

        if role == "admin":
            return {"message": f"Welcome back {username}!", "role": role}

        else:
            access_token = create_access_token({"sub": email, "role": role})
            return {
                "message": f"Welcome back, {username}!",
                "access_token": access_token,
                "token_type": "bearer",
                "role": role,
            }
    else:
        otp = random.randint(100000, 999999)
        expiry_time = datetime.utcnow() + timedelta(minutes=5)
        user_collection.insert_one(
            {"email": email, "otp": otp, "otp_expiry": expiry_time}
        )

        message_text = f"Your OTP code is: {otp}. It expires in 5 minutes."

        message = MessageSchema(
            subject="Your OTP Code",
            recipients=[email],
            body=message_text,
            subtype="plain",  # type:ignore
        )
        await fast_mail.send_message(message)

        return {"message": "OTP sent successfully"}


@router.post("/verify-otp")
async def verify_otp(request: OtpVerification):
    user = user_collection.find_one({"email": request.email})
    if (
        not user
        or user.get("otp") != request.otp
        or user.get("otp_expiry") < datetime.utcnow()
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user_collection.update_one(
        {"email": request.email}, {"$unset": {"otp": "", "otp_expiry": ""}}
    )

    user_collection.update_one(
        {"email": request.email}, {"$set": {"is_verified": True}}
    )

    if "user_id" not in user:
        new_user_id = generate_user_id()
        user_collection.update_one(
            {"email": request.email},
            {
                "$set": {
                    "user_id": new_user_id,
                    "username": request.email.split("@")[0],
                    "role": "user",
                    "is_verified": True,
                }
            },
        )

    access_token = create_access_token({"sub": request.email})

    home_url = ""

    return {
        "verified": True,
        "access_token": access_token,
        "token_type": "bearer",
        "redirect_url": home_url,
        "message": "User verified successfully",
    }
