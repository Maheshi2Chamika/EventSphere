
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.agents.notification_agent import NotificationAgent


# Create separate test database
engine = create_engine(
    "sqlite:///./notification_test.db",
    connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

TestingSession = sessionmaker(bind=engine)
db = TestingSession()


# Create test user
user = models.User(
    username="notificationuser",
    email="notification@example.com",
    password="test123"
)

db.add(user)
db.commit()
db.refresh(user)


# Test Notification Agent
agent = NotificationAgent()

notification = agent.send_notification(
    db=db,
    user_id=user.id,
    title="Booking Confirmation",
    message="Your event booking has been received."
)

print("Notification created!")
print("Title:", notification.title)
print("Message:", notification.message)
print("Is read:", notification.is_read)


# Retrieve notifications
notifications = agent.get_user_notifications(
    db=db,
    user_id=user.id
)

print("Total notifications:", len(notifications))


# Mark notification as read
updated = agent.mark_as_read(
    db=db,
    notification_id=notification.id
)

print("Notification marked as read:", updated.is_read)

db.close()
