from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
import os

app = FastAPI(title="Skilling & Alumni Impact Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# DATABASE
# =========================================================

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is missing")

client = MongoClient(MONGO_URI)
db = client["skilling_database"]

candidates_collection = db["candidates"]
checkins_collection = db["checkins"]
jobs_collection = db["jobs"]
mentors_collection = db["mentors"]
mentorship_collection = db["mentorship"]
certificates_collection = db["certificates"]
reviews_collection = db["reviews"]


# =========================================================
# MODELS
# =========================================================

class Candidate(BaseModel):
    name: str
    training_scheme: str
    course: str = ""
    placed: bool = False


class TrainingUpdate(BaseModel):
    candidate_id: str
    progress: int
    status: str


class Certificate(BaseModel):
    candidate_id: str
    course: str
    certificate_id: str


class CheckIn(BaseModel):
    candidate_id: str
    period: str
    employed: bool
    company: str = ""
    job_role: str = ""
    salary: float = 0
    skills_used: bool = False
    promotion: bool = False
    training_needed: str = ""


class EmployerVerification(BaseModel):
    candidate_id: str
    company: str
    job_role: str
    salary: float


class Job(BaseModel):
    title: str
    company: str
    location: str
    skills: list[str]
    salary: float = 0


class Mentor(BaseModel):
    name: str
    profession: str
    skills: list[str]
    location: str = ""


class MentorshipRequest(BaseModel):
    candidate_id: str
    mentor_id: str


# =========================================================
# HELPER
# =========================================================

def serialize(document):
    if not document:
        return None

    document["_id"] = str(document["_id"])
    return document


# =========================================================
# 1. CANDIDATE REGISTRATION
# =========================================================

@app.post("/register")
def register_candidate(candidate: Candidate):

    data = candidate.dict()

    data["training_progress"] = 0
    data["certified"] = False
    data["placement_verified"] = False
    data["created_at"] = datetime.utcnow()

    result = candidates_collection.insert_one(data)

    return {
        "message": "Candidate registered successfully",
        "candidate_id": str(result.inserted_id)
    }


# =========================================================
# 2. GET CANDIDATES
# =========================================================

@app.get("/candidates")
def get_candidates():

    candidates = []

    for candidate in candidates_collection.find():
        candidates.append(serialize(candidate))

    return candidates


# =========================================================
# 3. UPDATE PLACEMENT
# =========================================================

@app.put("/candidates/{candidate_id}/placement")
def update_placement(candidate_id: str, placed: bool):

    result = candidates_collection.update_one(
        {"_id": ObjectId(candidate_id)},
        {
            "$set": {
                "placed": placed
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return {
        "message": "Placement status updated"
    }


# =========================================================
# 4. TRAINING PROGRESS
# =========================================================

@app.post("/training/progress")
def update_training(data: TrainingUpdate):

    result = candidates_collection.update_one(
        {"_id": ObjectId(data.candidate_id)},
        {
            "$set": {
                "training_progress": data.progress,
                "training_status": data.status
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return {
        "message": "Training progress updated"
    }


# =========================================================
# 5. CERTIFICATION
# =========================================================

@app.post("/certification")
def add_certificate(data: Certificate):

    certificate = {
        "candidate_id": data.candidate_id,
        "course": data.course,
        "certificate_id": data.certificate_id,
        "verified": True,
        "created_at": datetime.utcnow()
    }

    certificates_collection.insert_one(certificate)

    candidates_collection.update_one(
        {"_id": ObjectId(data.candidate_id)},
        {
            "$set": {
                "certified": True
            }
        }
    )

    return {
        "message": "Certificate added and verified"
    }


# =========================================================
# 6. CAREER CHECK-IN
# =========================================================

@app.post("/checkin")
def career_checkin(data: CheckIn):

    allowed_periods = [
        "3_months",
        "6_months",
        "12_months",
        "24_months"
    ]

    if data.period not in allowed_periods:
        raise HTTPException(
            status_code=400,
            detail="Invalid check-in period"
        )

    checkin = data.dict()

    checkin["verified"] = False
    checkin["created_at"] = datetime.utcnow()

    result = checkins_collection.insert_one(checkin)

    return {
        "message": f"{data.period} check-in submitted",
        "checkin_id": str(result.inserted_id)
    }


# =========================================================
# 7. GET CANDIDATE CHECK-INS
# =========================================================

@app.get("/checkins/{candidate_id}")
def get_checkins(candidate_id: str):

    data = list(
        checkins_collection.find(
            {"candidate_id": candidate_id}
        )
    )

    return [serialize(x) for x in data]


# =========================================================
# 8. EMPLOYER VERIFICATION
# =========================================================

@app.post("/employer/verify-placement")
def verify_placement(data: EmployerVerification):

    result = candidates_collection.update_one(
        {"_id": ObjectId(data.candidate_id)},
        {
            "$set": {
                "placed": True,
                "placement_verified": True,
                "company": data.company,
                "job_role": data.job_role,
                "salary": data.salary,
                "verified_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return {
        "message": "Placement verified by employer"
    }


# =========================================================
# 9. JOB POSTING
# =========================================================

@app.post("/jobs")
def create_job(job: Job):

    result = jobs_collection.insert_one(
        job.dict()
    )

    return {
        "message": "Job created",
        "job_id": str(result.inserted_id)
    }


# =========================================================
# 10. GET JOBS
# =========================================================

@app.get("/jobs")
def get_jobs():

    jobs = list(jobs_collection.find())

    return [serialize(x) for x in jobs]


# =========================================================
# 11. SIMPLE JOB MATCHING
# =========================================================

@app.get("/jobs/match/{candidate_id}")
def match_jobs(candidate_id: str):

    candidate = candidates_collection.find_one(
        {"_id": ObjectId(candidate_id)}
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    candidate_skills = set(
        candidate.get("skills", [])
    )

    jobs = list(jobs_collection.find())

    recommendations = []

    for job in jobs:

        job_skills = set(job.get("skills", []))

        matching_skills = candidate_skills.intersection(
            job_skills
        )

        score = len(matching_skills)

        recommendations.append({
            **serialize(job),
            "match_score": score
        })

    recommendations.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return recommendations


# =========================================================
# 12. ALUMNI / MENTOR
# =========================================================

@app.post("/mentors")
def create_mentor(mentor: Mentor):

    result = mentors_collection.insert_one(
        mentor.dict()
    )

    return {
        "message": "Mentor registered",
        "mentor_id": str(result.inserted_id)
    }


@app.get("/mentors")
def get_mentors():

    mentors = list(mentors_collection.find())

    return [serialize(x) for x in mentors]


# =========================================================
# 13. MENTORSHIP REQUEST
# =========================================================

@app.post("/mentorship/request")
def mentorship_request(data: MentorshipRequest):

    request_data = {
        "candidate_id": data.candidate_id,
        "mentor_id": data.mentor_id,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = mentorship_collection.insert_one(
        request_data
    )

    return {
        "message": "Mentorship request sent",
        "request_id": str(result.inserted_id)
    }


# =========================================================
# 14. IMPACT DASHBOARD
# =========================================================

@app.get("/dashboard/impact")
def impact_dashboard():

    total = candidates_collection.count_documents({})

    placed = candidates_collection.count_documents(
        {"placed": True}
    )

    certified = candidates_collection.count_documents(
        {"certified": True}
    )

    verified = candidates_collection.count_documents(
        {"placement_verified": True}
    )

    placement_rate = 0
    certification_rate = 0
    verification_rate = 0

    if total:
        placement_rate = round(
            (placed / total) * 100,
            2
        )

        certification_rate = round(
            (certified / total) * 100,
            2
        )

        verification_rate = round(
            (verified / total) * 100,
            2
        )

    return {
        "total_candidates": total,
        "placed_candidates": placed,
        "certified_candidates": certified,
        "verified_placements": verified,
        "placement_rate": placement_rate,
        "certification_rate": certification_rate,
        "verification_rate": verification_rate
    }


# =========================================================
# 15. CHECK-IN IMPACT
# =========================================================

@app.get("/dashboard/retention")
def retention_dashboard():

    result = {}

    for period in [
        "3_months",
        "6_months",
        "12_months",
        "24_months"
    ]:

        total = checkins_collection.count_documents(
            {"period": period}
        )

        employed = checkins_collection.count_documents(
            {
                "period": period,
                "employed": True
            }
        )

        rate = 0

        if total:
            rate = round(
                (employed / total) * 100,
                2
            )

        result[period] = {
            "responses": total,
            "employed": employed,
            "employment_rate": rate
        }

    return result
