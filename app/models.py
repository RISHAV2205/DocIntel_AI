from .database import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime,Text
from sqlalchemy.sql.expression import null,text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from pgvector.sqlalchemy import Vector

class post(Base):
    __tablename__="posts"
    
    id =Column(Integer,primary_key=True,nullable=False)
    title=Column(String,nullable=False)
    content=Column(String,nullable=False)
    published=Column(Boolean,server_default="True",nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text("now()"))
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    owner = relationship("user", back_populates="posts")

    
class user(Base):
    __tablename__="users"
    email=Column(String,nullable=False,unique=True)
    password=Column(String,nullable=False)
    id =Column(Integer,primary_key=True,nullable=False,autoincrement=True)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text("now()"))
    posts = relationship("post", back_populates="owner")
    chats = relationship("Chat",backref="owner",cascade="all, delete-orphan")
    
    
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    extracted_text_path = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(String, default="uploaded")  # uploaded | processing | ready | failed for asynchronos task
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )    


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(Vector(384), nullable=True)

    # Relationship
    document = relationship("Document", back_populates="chunks")
    

class Chat(Base):
    __tablename__ = "chats"
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True
    )
    title = Column(
        String,
        default="New Chat"
    )
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )
    # Relationship
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan"
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True
    )

    chat_id = Column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    # Relationship
    chat = relationship(
        "Chat",
        back_populates="messages"
    )