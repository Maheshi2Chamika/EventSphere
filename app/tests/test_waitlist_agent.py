
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.agents.waitlist_agent import WaitlistAgent


# Create separate test database
engine = create_engine(
    "sqlite:///./waitlist_test.db",
    connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

TestingSession = sessionmaker(bind=engine)
db = TestingSession()


# Create test user
user = models.User(
    username="waitlistuser",
    email="waitlist@example.com",
    password="test123"
)

db.add(user)
db.commit()
db.refresh(user)


# Test Waitlist Agent
agent = WaitlistAgent()

message = agent.add_to_waitlist(
    db=db,
    user_id=user.id,
    message_text="I want to join the event waitlist."
)

print("Waitlist request created!")
print("Message:", message.message_text)
print("Sender:", message.sender)

messages = agent.get_waitlist_messages(db)

print("Total waitlist messages:", len(messages))

db.close()
