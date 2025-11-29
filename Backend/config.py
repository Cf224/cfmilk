from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# import os

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# DATABASE_URL = os.getenv("DATABASE_URL")
# ADMIN_PHONE = os.getenv("ADMIN_PHONE")

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")

SECRET_KEY = ""
ALGORITHM = "HS256"

# USERNAME = os.getenv("USERNAME") 
# HOST = os.getenv("HOST")
# DB_NAME = os.getenv("DB_NAME")
# PASSWORD = os.getenv("PASSWORD")

# DATABASE_URL = f"mysql+mysqlconnector://sql12804224:{PASSWORD}@{HOST}/{DB_NAME}"
# DATABASE_URL = "mysql+mysqlconnector://root:DsfkAEQIibDpMesuyeeKScDLfZoTYXDq@yamanote.proxy.rlwy.net:59130/railway"
# DATABASE_URL = "mysql+mysqlconnector://root:Test%40123@localhost/cf_milk"
# DATABASE_URL = "mysql+mysqlconnector://root:Test%40123@localhost/cf_milk"

CA_PATH = "D:\\CF_Milk_Api\\Backend\\isrgrootx1.pem"
T = True
# &ssl_verify_cert={T}&ssl_verify_identity={T}
DATABASE_URL = f"mysql+mysqlconnector://6b6VzSB1uicmb9w.root:ux8FViNRiPf2p7St@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/cf_milk?ssl_ca={CA_PATH}"

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