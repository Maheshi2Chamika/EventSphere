
import uuid

from sqlalchemy.orm import Session

from app.models import Ticket


class TicketAgent:

    def generate_tickets(
        self,
        db: Session,
        booking_id: int,
        quantity: int
    ):
        # Check whether tickets already exist
        existing_tickets = db.query(Ticket).filter(
            Ticket.booking_id == booking_id
        ).all()

        # Return existing tickets if available
        if existing_tickets:
            return existing_tickets

        tickets = []

        # Generate new tickets
        for _ in range(quantity):
            ticket = Ticket(
                ticket_code=str(uuid.uuid4()),
                booking_id=booking_id,
                is_checked_in=False
            )

            db.add(ticket)
            tickets.append(ticket)

        db.commit()

        for ticket in tickets:
            db.refresh(ticket)

        return tickets

    def check_in_ticket(
        self,
        db: Session,
        ticket_code: str
    ):
        ticket = db.query(Ticket).filter(
            Ticket.ticket_code == ticket_code
        ).first()

        if not ticket:
            raise ValueError("Ticket not found")

        if ticket.is_checked_in:
            raise ValueError("Ticket already checked in")

        ticket.is_checked_in = True

        db.commit()
        db.refresh(ticket)

        return ticket
