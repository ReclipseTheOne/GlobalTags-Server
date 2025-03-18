from fastapi import FastAPI, HTTPException, Depends, Body

from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Integer, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv


# Database setup
DATABASE_URL = "sqlite:///./tags.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI setup
app = FastAPI()
load_dotenv('.env')


### MODELS ###

# Tag model
class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    message = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    owner_id = Column(String, nullable=False)


# Create the database tables
Base.metadata.create_all(bind=engine)


# Pydantic schema for validation
class TagSchema(BaseModel):
    name: str
    message: str
    owner: str
    owner_id: str
    key: str

    class Config:
        orm_mode = True
        from_attributes = True


# Pydantic schema for response
class TagResponseSchema(BaseModel):
    name: str
    message: str
    owner_id: str

    class Config:
        orm_mode = True
        from_attributes = True


# Pydantic schema for delete
class DeleteTagSchema(BaseModel):
    key: str

    class Config:
        orm_mode = True
        from_attributes = True


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get("/tags", response_model=List[TagResponseSchema])
def get_tags(db=Depends(get_db)):
    return db.query(Tag).all()


@app.get("/tags/{name}", response_model=TagResponseSchema)
def get_tag(name: str, db=Depends(get_db)):
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.post("/tags", response_model=dict)
def create_tag(tag: TagSchema, db=Depends(get_db)):
    if tag.key != os.environ.get("DATABASE_KEY"):
        return {"success": False, "error": "Invalid key. Access denied."}
    if tag.name in [t.name for t in db.query(Tag).all()]:
        return {"success": False, "error": "Tag already exists"}

    db_tag = Tag(name=tag.name, message=tag.message, owner=tag.owner, owner_id=tag.owner_id)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return {"success": True, "data": TagResponseSchema.model_validate(db_tag)}


@app.delete("/tags/{name}", response_model=dict)
def delete_tag(name: str, delete_tag: DeleteTagSchema = Body(...), db=Depends(get_db)):
    if delete_tag.key != os.environ.get("DATABASE_KEY"):
        return {"success": False, "error": "Invalid key. Access denied."}

    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        return {"success": False, "error": "Tag does not exist."}

    db.delete(tag)
    db.commit()
    return {"success": True}
