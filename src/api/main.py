from fastapi import FastAPI, WebSocket, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import json

from src.database.connection import get_db, get_redis
from src.database.models import User, Classroom, StreamMetadata
from src.api.auth import (
    get_current_user,
    create_access_token,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI()

# Authentication endpoints
@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=dict)
async def register(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

# Classroom endpoints
@app.post("/classrooms")
async def create_classroom(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    classroom = Classroom(
        name=name,
        teacher_id=current_user.id,
        rtmp_key=f"{current_user.username}_{name.lower().replace(' ', '_')}"
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return classroom

@app.get("/classrooms")
async def get_classrooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Classroom).filter(Classroom.teacher_id == current_user.id).all()

# Stream endpoints
@app.get("/streams")
async def get_streams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(StreamMetadata).join(Classroom).filter(
        Classroom.teacher_id == current_user.id
    ).all()

# WebSocket endpoint for stream status updates
@app.websocket("/ws/stream-status")
async def stream_status_websocket(
    websocket: WebSocket,
    redis = Depends(get_redis)
):
    await websocket.accept()
    pubsub = redis.pubsub()
    await pubsub.subscribe("stream_status_updates")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
    except Exception:
        await websocket.close()
    finally:
        await pubsub.unsubscribe("stream_status_updates")
