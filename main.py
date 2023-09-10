from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from typing import List

DATABASE_URL = "postgresql://postgres:password@localhost/fastapidatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str

class UserProfile(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str

@app.post("/register/", response_model=UserProfile)
async def register_user(user: UserCreate):
    db = SessionLocal()

    try:

        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")


        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Phone already registered")
    finally:
        db.close()

@app.get("/user/{user_id}/", response_model=UserProfile)
async def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=List[UserProfile])
async def get_all_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
