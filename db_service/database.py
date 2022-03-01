import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()  # take environment variables from .env.

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['LOG']}:{os.environ['PASS']}@{os.environ['HOST']}:5432/kaspi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
