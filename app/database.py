from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URL=os.getenv("SUPABASE_URL")

engine=create_engine(SQLALCHEMY_DATABASE_URL)

#factory that create db session,it is a session that make transaction with a db
session_local=sessionmaker(autocommit=False,autoflush=False,bind=engine)

#  Create the base class for ORM models
Base=declarative_base()

# cleanup if error occur
def get_db():  #dependency on session
    db=session_local()
    try:
        yield db
    finally:
        db.close()
