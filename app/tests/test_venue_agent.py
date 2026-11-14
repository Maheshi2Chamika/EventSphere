
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.agents.venue_agent import VenueAgent


# Create a separate test database
engine = create_engine(
    "sqlite:///./agent_test.db",
    connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

TestingSession = sessionmaker(bind=engine)
db = TestingSession()


# Create test user
user = models.User(
    username="testuser",
    email="test@example.com",
    password="test123"
)

db.add(user)
db.commit()
db.refresh(user)


# Create test venue
venue = models.Venue(
    name="University Auditorium",
    location="Vavuniya",
    capacity=500,
    description="Test venue",
    is_available=True
)

db.add(venue)
db.commit()
db.refresh(venue)


# Test Venue Agent
agent = VenueAgent()

venues = agent.get_available_venues(db)

print("Available venues:", len(venues))

request = agent.create_hire_request(
    db=db,
    user_id=user.id,
    venue_id=venue.id,
    event_name="Tech Conference",
    requested_date=datetime(2026, 12, 1, 10, 0),
    expected_attendees=200
)

print("Hire request created!")
print("Event:", request.event_name)
print("Status:", request.status)

db.close()
