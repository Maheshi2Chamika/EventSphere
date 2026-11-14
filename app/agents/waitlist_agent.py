
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Message


class WaitlistAgent:

    def add_to_waitlist(
        self,
        db: Session,
        user_id: int,
        message_text: str
    ):

        message = Message(
            user_id=user_id,
            message_text=message_text,
            sender="attendee",
            created_at=datetime.now()
)

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    def get_waitlist_messages(self, db: Session):

        messages = db.query(Message).filter(
            Message.sender == "attendee"
        ).order_by(Message.id.asc()).all()

        return messages
