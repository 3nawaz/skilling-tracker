from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

# Allow your HTML file to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Atlas connection string
MONGO_URI = "mongodb+srv://muzffarnawazalam_db_user:WJqFi5WKr3sL9b8a@cluster0.vsiguh9.mongodb.net/?appName=Cluster0" # Ensure this is your Atlas URI
client = MongoClient(MONGO_URI)
db = client["skilling_database"]
candidates_collection = db["candidates"]

class Candidate(BaseModel):
    name: str
    training_scheme: str
    placed: bool

@app.post("/register")
def register_candidate(candidate: Candidate):
    candidate_data = candidate.dict()
    candidate_data["retention_verified"] = False 
    candidates_collection.insert_one(candidate_data)
    return {"message": "Success"}

@app.get("/candidates")
def get_candidates():
    # Retrieve all records, ignoring the MongoDB specific '_id' object
    candidates = list(candidates_collection.find({}, {"_id": 0}))
    return candidates