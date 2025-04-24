from fastapi import FastAPI, HTTPException, Depends, Form, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from pymongo import MongoClient
from passlib.context import CryptContext
import os
from starlette.middleware.sessions import SessionMiddleware

# Initialize FastAPI
app = FastAPI(title="Golf Score Tracker API")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-for-development")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/golf_tracker")
client = MongoClient(MONGO_URI)
db = client.golf_tracker
users_collection = db.users
scorecards_collection = db.scorecards

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class Hole(BaseModel):
    number: int
    par: int
    score: int

class ScoreCard(BaseModel):
    id: str
    date_played: str
    course_name: str
    holes: List[Hole]
    notes: Optional[str] = None
    weather: Optional[str] = None
    user_id: Optional[str] = None

class ScoreCardCreate(BaseModel):
    date_played: str
    course_name: str
    holes: List[Hole]
    notes: Optional[str] = None
    weather: Optional[str] = None

class ScoreCardUpdate(BaseModel):
    date_played: Optional[str] = None
    course_name: Optional[str] = None
    holes: Optional[List[Hole]] = None
    notes: Optional[str] = None
    weather: Optional[str] = None

class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

# Helper functions
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

# Dependency to get current user
async def get_current_user(request: Request):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Auth routes
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Set session data
    request.session["username"] = username
    request.session["user_id"] = str(user["_id"])
    
    return {"message": "Login successful"}

@app.post("/register")
async def register(user: User):
    # Check if username exists
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "password": hashed_password,
        "email": user.email,
        "created_at": datetime.utcnow()
    }
    
    result = users_collection.insert_one(user_data)
    return {"message": "User registered successfully"}

@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logout successful"}

@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user.get("email", "")
    }

# Scorecard routes
@app.post("/scorecards/", response_model=ScoreCard)
async def create_scorecard(scorecard: ScoreCardCreate, current_user: dict = Depends(get_current_user)):
    scorecard_id = str(uuid.uuid4())
    
    # Create scorecard
    new_scorecard = {
        "id": scorecard_id,
        "date_played": scorecard.date_played,
        "course_name": scorecard.course_name,
        "holes": [hole.dict() for hole in scorecard.holes],
        "notes": scorecard.notes,
        "weather": scorecard.weather,
        "user_id": str(current_user["_id"])
    }
    
    # Insert into MongoDB
    scorecards_collection.insert_one(new_scorecard)
    
    return ScoreCard(**new_scorecard)

@app.get("/scorecards/", response_model=List[ScoreCard])
async def read_scorecards(current_user: dict = Depends(get_current_user)):
    # Get scorecards for current user
    user_scorecards = list(scorecards_collection.find({"user_id": str(current_user["_id"])}))
    return [ScoreCard(**scorecard) for scorecard in user_scorecards]

@app.get("/scorecards/{scorecard_id}", response_model=ScoreCard)
async def read_scorecard(scorecard_id: str, current_user: dict = Depends(get_current_user)):
    # Get specific scorecard
    scorecard = scorecards_collection.find_one({
        "id": scorecard_id,
        "user_id": str(current_user["_id"])
    })
    
    if not scorecard:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    
    return ScoreCard(**scorecard)

@app.put("/scorecards/{scorecard_id}", response_model=ScoreCard)
async def update_scorecard(scorecard_id: str, scorecard_update: ScoreCardUpdate, current_user: dict = Depends(get_current_user)):
    # Check if scorecard exists
    existing_scorecard = scorecards_collection.find_one({
        "id": scorecard_id,
        "user_id": str(current_user["_id"])
    })
    
    if not existing_scorecard:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    
    # Update fields
    update_data = {k: v for k, v in scorecard_update.dict().items() if v is not None}
    
    if 'holes' in update_data:
        update_data['holes'] = [hole.dict() for hole in update_data['holes']]
    
    scorecards_collection.update_one(
        {"id": scorecard_id, "user_id": str(current_user["_id"])},
        {"$set": update_data}
    )
    
    # Get updated scorecard
    updated_scorecard = scorecards_collection.find_one({
        "id": scorecard_id,
        "user_id": str(current_user["_id"])
    })
    
    return ScoreCard(**updated_scorecard)

@app.delete("/scorecards/{scorecard_id}")
async def delete_scorecard(scorecard_id: str, current_user: dict = Depends(get_current_user)):
    # Check if scorecard exists
    existing_scorecard = scorecards_collection.find_one({
        "id": scorecard_id,
        "user_id": str(current_user["_id"])
    })
    
    if not existing_scorecard:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    
    # Delete scorecard
    scorecards_collection.delete_one({"id": scorecard_id, "user_id": str(current_user["_id"])})
    
    return {"message": "Scorecard deleted successfully"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Golf Score Tracker API"}

# Run on startup
@app.on_event("startup")
async def startup_event():
    # Create indexes
    users_collection.create_index("username", unique=True)