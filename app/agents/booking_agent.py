
from sqlalchemy.orm import Session

from app.models import Booking, TicketCategory


class BookingAgent:

    def create_booking(
        self,
        db: Session,
        user_id: int,
        event_id: int,
        ticket_category_id: int,
        quantity: int
    ):

        # Find the selected ticket category
        category = db.query(TicketCategory).filter(
            TicketCategory.id == ticket_category_id,
            TicketCategory.event_id == event_id
        ).first()

        if not category:
            raise ValueError("Ticket category not found")

        # Check available ticket quantity
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if quantity > category.quantity:
            raise ValueError("Not enough tickets available")

        # Calculate total price
        total_price = category.price * quantity

        # Create booking
        booking = Booking(
            user_id=user_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=quantity,
            total_price=total_price,
            status="pending"
        )

        # Save booking
        db.add(booking)

        # Reduce available ticket quantity
        category.quantity -= quantity

        db.commit()
        db.refresh(booking)

        return booking
