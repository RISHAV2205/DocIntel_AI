from jose import JWTError,jwt
from datetime import timezone,datetime,timedelta
from . import schema
from fastapi import Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer
import os

from dotenv import load_dotenv
load_dotenv() 

# When we create an instance of the OAuth2PasswordBearer class we pass in the tokenUrl parameter. This parameter contains the URL that the client (the frontend running in the user's browser) will use to send the username and password in order to get a token.
# “Users will send username/password to /login endpoint to get a token.”
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")  #auth login url
# oauth2_scheme
# ONLY extracts the token.

#SECRET KEY
#ALGORITHM
#EXPIRATION TIME
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# print("SECRET_KEY:", SECRET_KEY, type(SECRET_KEY))

def create_access_token(data:dict):
    to_encode=data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    # print(to_encode)
    
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    
    return encoded_jwt
    
    
def verify_access_token(token:str,credential_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id: str=payload.get("user_id")
    
        if user_id is None:
            raise credential_exception
        token_data=schema.TokenData(id=user_id)
    except JWTError:
        raise credential_exception
    return token_data
        
def get_current_user(token:str=Depends(oauth2_scheme)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"couldnot validate credentials",headers={"WWW-Authenticate":"Bearer"})
    return verify_access_token(token,credentials_exception)





# '''27. Full Authentication Flow
# LOGIN

# User sends:

# username + password
# TOKEN CREATION
# create_access_token()

# returns JWT.

# FRONTEND STORES TOKEN

# Usually:

# localStorage
# cookies
# PROTECTED REQUEST
# Authorization: Bearer <token>
# FASTAPI EXTRACTS TOKEN

# Using:

# oauth2_scheme
# TOKEN VERIFIED

# Using:

# verify_access_token()
# CURRENT USER RETURNED

# Using:

# get_current_user()
# 28. Typical Protected Route
# @app.get("/users/me")
# def get_user(current_user = Depends(get_current_user)):
#     return current_user

# Now route automatically becomes protected.

# 29. Industry-Level Architecture

# Your code already follows real-world backend architecture used in:

# SaaS apps
# AI platforms
# Banking APIs
# Microservices
# Production FastAPI systems
# 30. One Important Improvement

# Right now:

# user_id: str

# But IDs are usually integers.

# Better:

# user_id: int

# and:

# class TokenData(BaseModel):
#     id: int
# 31. Final Mental Model

# Your auth.py works like this:

# LOGIN
#    ↓
# Generate JWT
#    ↓
# Client stores JWT
#    ↓
# Client sends JWT
#    ↓
# FastAPI extracts JWT
#    ↓
# JWT verified
#    ↓
# Current user identified
#    ↓
# Protected route allowed

# This is the foundation of JWT authentication in FastAPI.'''