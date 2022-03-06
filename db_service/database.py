import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()  # take environment variables from .env.

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ['LOG']}:" \
                          f"{os.environ['PASS']}@{os.environ['HOST']}:" \
                          f"{os.environ['PORT']}/{os.environ['DATABASE_NAME']}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

if __name__ == '__main__':
    engine