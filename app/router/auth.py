from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database,models,schema,utils,oauth2

router=APIRouter(tags=["authentication"])

@router.post("/login")
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(database.get_db)):
    
    # OAuth2PasswordRequestForm return dict of username and password and instead of body we will pass in a form data in postman
    user=db.query(models.user).filter(models.user.email==user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"invalid credentials")
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"invalid credentials")
    
    # if password is corrrect
    # create token
    # valid token
    access_token=oauth2.create_access_token(data={"user_id":str(user.id)})
    
    return {"access_token":access_token,"token_type":"bearer"}

    

