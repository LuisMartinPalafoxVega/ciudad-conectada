from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Connection
#DATABASE_URL = os.getenv(
 #   "DATABASE_URL",
  #  "mysql+pymysql://root:root@localhost:3306/ciudad_conectada"
#)
MYSQL_USER = "root"
MYSQL_PASSWORD= "BwEVcwXZPUGHtwtyZpCcZWOreNobiEKg"
MYSQL_HOST= "mysql.railway.internal"
MYSQL_PORT = "3306"
MYSQL_DB = "railway"


DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()