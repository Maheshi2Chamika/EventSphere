
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.agents.ticket_agent import TicketAgent


# Create separate test database
engine = create_engine(
    "sqlite:///./ticket_test.db",
    connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

TestingSession = sessionmaker(bind=engine)
db = TestingSession()


# Create test user
user = models.User(
    username="ticketuser",
    email="ticket@example.com",
    password="test123"
)

db.add(user)
db.commit()
db.refresh(user)


# Create a booking
booking = models.Booking(
    user_id=user.id,
    event_id=1,
    ticket_category_id=1,
    quantity=2,
    total_price=2000,
    status="pending"
)

db.add(booking)
db.commit()
db.refresh(booking)


# Test Ticket Agent
agent = TicketAgent()

tickets = agent.generate_tickets(
    db=db,
    booking_id=booking.id,
    quantity=2
)

print("Tickets generated:", len(tickets))
print("Ticket 1 code:", tickets[0].ticket_code)
print("Ticket 2 code:", tickets[1].ticket_code)

# Test check-in
checked_ticket = agent.check_in_ticket(
    db=db,
    ticket_code=tickets[0].ticket_code
)

print("Ticket checked in:", checked_ticket.is_checked_in)

# Test duplicate check-in
try:
    agent.check_in_ticket(
        db=db,
        ticket_code=tickets[0].ticket_code
    )
except ValueError as error:
    print("Duplicate check-in prevented:", error)

db.close()
