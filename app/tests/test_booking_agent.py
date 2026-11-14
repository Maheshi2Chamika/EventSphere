
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.agents.booking_agent import BookingAgent


# Create separate test database
engine = create_engine(
    "sqlite:///./booking_test.db",
    connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

TestingSession = sessionmaker(bind=engine)
db = TestingSession()


# Create test user
user = models.User(
    username="bookinguser",
    email="booking@example.com",
    password="test123"
)

db.add(user)
db.commit()
db.refresh(user)


# Create venue
venue = models.Venue(
    name="Main Hall",
    location="Vavuniya",
    capacity=300,
    is_available=True
)

db.add(venue)
db.commit()
db.refresh(venue)


# Create event
event = models.Event(
    title="Python Workshop",
    description="Programming workshop",
    event_date=datetime(2026, 12, 10),
    venue_id=venue.id,
    organizer_id=user.id
)

db.add(event)
db.commit()
db.refresh(event)


# Create ticket category
category = models.TicketCategory(
    name="Regular",
    price=1000,
    quantity=50,
    event_id=event.id
)

db.add(category)
db.commit()
db.refresh(category)


# Test Booking Agent
agent = BookingAgent()

booking = agent.create_booking(
    db=db,
    user_id=user.id,
    event_id=event.id,
    ticket_category_id=category.id,
    quantity=2
)

print("Booking created successfully!")
print("Booking ID:", booking.id)
print("Quantity:", booking.quantity)
print("Total price:", booking.total_price)
print("Booking status:", booking.status)

db.refresh(category)
print("Remaining tickets:", category.quantity)

db.close()
