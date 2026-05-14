from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

import models, schemas, auth_utils
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Language Trainer API")

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Хешируем пароль
    hashed_pass = auth_utils.get_password_hash(user.password)

    # Создаем объект пользователя для БД
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pass,
        level=user.level
    )

    # Сохраняем в БД
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()

    if not user or not auth_utils.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT токен
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {"message": "AI Language Trainer API is running"}