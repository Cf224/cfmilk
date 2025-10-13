from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_PHONE = os.getenv("ADMIN_PHONE")

SECRET_KEY = ""
ALGORITHM = "HS256"

USERNAME = "root"
PASSWORD = "Test%40123"
HOST = "localhost:3306"
DB_NAME = "cf_milk"

DATABASE_URL = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DB_NAME}"


engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


try:
    with engine.connect() as connection:
        print("Database Connected Successfully..!")
except Exception as e:
    print("Databadw Unable to connected",e)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 