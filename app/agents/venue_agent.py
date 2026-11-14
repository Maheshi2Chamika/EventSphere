
from sqlalchemy.orm import Session

from app.models import Venue, VenueHireRequest


class VenueAgent:

    def get_available_venues(self, db: Session):
        venues = db.query(Venue).filter(
            Venue.is_available == True
        ).all()

        return venues

    def create_hire_request(
        self,
        db: Session,
        user_id: int,
        venue_id: int,
        event_name: str,
        requested_date,
        expected_attendees: int
    ):

        venue = db.query(Venue).filter(
            Venue.id == venue_id
        ).first()

        if not venue:
            raise ValueError("Venue not found")

        if not venue.is_available:
            raise ValueError("Venue is not available")

        if expected_attendees > venue.capacity:
            raise ValueError("Venue capacity exceeded")

        request = VenueHireRequest(
            user_id=user_id,
            venue_id=venue_id,
            event_name=event_name,
            requested_date=requested_date,
            expected_attendees=expected_attendees,
            status="pending"
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        return request
