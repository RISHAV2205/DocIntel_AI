from fastapi import FastAPI,Response,status,HTTPException,Depends
from .router import post, user,auth,documents,query,chat,chat_message
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI()

    
#communicate with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(chat.router)
app.include_router(chat_message.router)