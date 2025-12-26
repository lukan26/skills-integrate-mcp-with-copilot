"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from database import get_db, engine, Base
from models import Activity, Participant
from init_db import init_database

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their participants"""
    activities = db.query(Activity).all()
    return {activity.name: activity.to_dict() for activity in activities}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if participant exists, create if not
    participant = db.query(Participant).filter(Participant.email == email).first()
    if not participant:
        participant = Participant(email=email)
        db.add(participant)

    # Validate student is not already signed up
    if participant in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student to activity
    activity.participants.append(participant)
    db.commit()

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Find participant
    participant = db.query(Participant).filter(Participant.email == email).first()
    if not participant or participant not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student from activity
    activity.participants.remove(participant)
    db.commit()

    return {"message": f"Unregistered {email} from {activity_name}"}
