from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL='postgresql://postgres:1234@localhost/FastAPI'

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
