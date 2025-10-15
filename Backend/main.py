from fastapi import FastAPI
from Backend.config import engine,Base,SessionLocal
from Backend.Routes.auth import router
from Backend.Routes.admin import admin_router
from Backend.Routes.customer import customer_router

app = FastAPI()


# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.include_router(router)
app.include_router(admin_router)
app.include_router(customer_router)

@app.get('/')
def Root():
    return {"Hello Buddy....!"}