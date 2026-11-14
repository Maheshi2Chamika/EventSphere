
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app import models, schemas
from app.agents.venue_agent import VenueAgent


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="EventSphere",
    description="Multi-Agent Venue Booking and Digital Ticketing Platform",
    version="1.0.0"
)


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create Venue Agent
venue_agent = VenueAgent()


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to EventSphere!"
    }


# Status endpoint
@app.get("/status")
def status():
    return {
        "status": "Running"
    }


# Create a venue
@app.post("/venues", response_model=schemas.VenueResponse)
def create_venue(
    venue: schemas.VenueCreate,
    db: Session = Depends(get_db)
):
    new_venue = models.Venue(**venue.model_dump())

    db.add(new_venue)
    db.commit()
    db.refresh(new_venue)

    return new_venue


# Get available venues
@app.get("/venues", response_model=list[schemas.VenueResponse])
def get_available_venues(
    db: Session = Depends(get_db)
):
    return venue_agent.get_available_venues(db)


# Create venue hire request
@app.post(
    "/venue-hire-requests",
    response_model=schemas.VenueHireRequestResponse
)
def create_venue_hire_request(
    request: schemas.VenueHireRequestCreate,
    db: Session = Depends(get_db)
):
    try:
        return venue_agent.create_hire_request(
            db=db,
            user_id=request.user_id,
            venue_id=request.venue_id,
            event_name=request.event_name,
            requested_date=request.requested_date,
            expected_attendees=request.expected_attendees
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
