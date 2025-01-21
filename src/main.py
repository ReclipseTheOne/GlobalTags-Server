from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Database setup
DATABASE_URL = "sqlite:///./tags.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
app = FastAPI()


# Tag model
class Tag(Base):
    __tablename__ = "tags"
    name = Column(String, primary_key=True, index=True)
    message = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)


# Pydantic schema for validation
class TagSchema(BaseModel):
    name: str
    message: str
    enabled: bool = True

    class Config:
        orm_mode = True


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Routes
@app.get("/tags", response_model=List[TagSchema])
def get_tags(db=next(get_db())):
    return db.query(Tag).all()


@app.get("/tags/{name}", response_model=TagSchema)
def get_tag(name: str, db=next(get_db())):
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.post("/tags", response_model=TagSchema)
def create_tag(tag: TagSchema, db=next(get_db())):
    db_tag = Tag(name=tag.name, message=tag.message, enabled=tag.enabled)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.delete("/tags/{name}", response_model=dict)
def delete_tag(name: str, db=next(get_db())):
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
    return {"success": True}
