from .. import models,database,schema,utils
from typing import Optional,List
from sqlalchemy.orm import Session
from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from .. database import session_local,get_db

router=APIRouter(prefix="/users",tags=["users"])


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schema.UserOut)
def create_users(user:schema.UserCreate,db:Session=Depends(get_db)):
    #hash the password
    existing_user = db.query(models.user).filter(
        models.user.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    hashed_password=utils.hash(user.password)
    user.password=hashed_password
    
    new_user=models.user(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}",response_model=schema.UserOut)
def get_users(id:int,db:Session=Depends(get_db)):
    user=db.query(models.user).filter(models.user.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with {id} not found")
    return user
    