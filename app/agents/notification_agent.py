
from sqlalchemy.orm import Session

from app.models import Notification


class NotificationAgent:

    def send_notification(
        self,
        db: Session,
        user_id: int,
        title: str,
        message: str
    ):

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            is_read=False
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    def get_user_notifications(
        self,
        db: Session,
        user_id: int
    ):

        notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).all()

        return notifications

    def mark_as_read(
        self,
        db: Session,
        notification_id: int
    ):

        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification:
            raise ValueError("Notification not found")

        notification.is_read = True

        db.commit()
        db.refresh(notification)

        return notification
