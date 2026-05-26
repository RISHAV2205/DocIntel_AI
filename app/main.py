from typing import Optional,List
from fastapi import FastAPI,Response,status,HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel  # it is used to validate schema coming from user
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models,schema,utils
from sqlalchemy.orm import Session
from .database import engine,session_local,get_db
from passlib.context import CryptContext
from .router import post, user,auth,documents,query,chat,chat_message

from fastapi.middleware.cors import CORSMiddleware
 
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# connect to database
while True:       
    try:
        conn=psycopg2.connect(host='localhost',database='FastAPI',user='postgres',password=1234,cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("connection was succesfull")
        break
    except Exception as error:
        print("connecting to database failed")
        print("error :", error)
        time.sleep(3)
    
#communicate with frontent
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# my_post=[{"title":"hello","content":"vjfjv","id":1}]

# def find_post(id):  #helpful in retrieving particular post
#     for p in my_post:
#         if p['id']==id:
#             return p
        
# def find_index_post(id):    #helpful in deleting particular post by searching index
#     for i,p in enumerate(my_post):
#         if p["id"]==id:
#             return i


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(chat.router)
app.include_router(chat_message.router)