
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app import models, schemas

from app.agents.venue_agent import VenueAgent
from app.agents.booking_agent import BookingAgent
from app.agents.ticket_agent import TicketAgent
from app.agents.waitlist_agent import WaitlistAgent
from app.agents.notification_agent import NotificationAgent


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="EventSphere",
    description="Multi-Agent Venue Booking and Digital Ticketing Platform",
    version="1.0.0"
)


# Serve frontend files
app.mount(
    "/frontend",
    StaticFiles(directory="app/frontend", html=True),
    name="frontend"
)


# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize agents
venue_agent = VenueAgent()
booking_agent = BookingAgent()
ticket_agent = TicketAgent()
waitlist_agent = WaitlistAgent()
notification_agent = NotificationAgent()


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to EventSphere!"
    }


# Status endpoint
@app.get("/status")
def status():
    return {
        "status": "Running"
    }



# -----------------------------
# VENUE APIs
# -----------------------------

# Create a venue
@app.post("/venues", response_model=schemas.VenueResponse)
def create_venue(
    venue: schemas.VenueCreate,
    db: Session = Depends(get_db)
):
    new_venue = models.Venue(**venue.model_dump())

    db.add(new_venue)
    db.commit()
    db.refresh(new_venue)

    return new_venue


# Get available venues
@app.get("/venues", response_model=list[schemas.VenueResponse])
def get_available_venues(
    db: Session = Depends(get_db)
):
    return venue_agent.get_available_venues(db)


# Create venue hire request
@app.post(
    "/venue-hire-requests",
    response_model=schemas.VenueHireRequestResponse
)
def create_venue_hire_request(
    request: schemas.VenueHireRequestCreate,
    db: Session = Depends(get_db)
):
    try:
        return venue_agent.create_hire_request(
            db=db,
            user_id=request.user_id,
            venue_id=request.venue_id,
            event_name=request.event_name,
            requested_date=request.requested_date,
            expected_attendees=request.expected_attendees
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# Get all venue hire requests
@app.get(
    "/venue-hire-requests",
    response_model=list[schemas.VenueHireRequestResponse]
)
def get_venue_hire_requests(
    db: Session = Depends(get_db)
):
    return db.query(models.VenueHireRequest).all()


# -----------------------------
# EVENT APIs
# -----------------------------

# Create an event
@app.post("/events", response_model=schemas.EventResponse)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db)
):
    venue = db.query(models.Venue).filter(
        models.Venue.id == event.venue_id
    ).first()

    if not venue:
        raise HTTPException(
            status_code=404,
            detail="Venue not found"
        )

    organizer = db.query(models.User).filter(
        models.User.id == event.organizer_id
    ).first()

    if not organizer:
        raise HTTPException(
            status_code=404,
            detail="Organizer not found"
        )

    new_event = models.Event(**event.model_dump())

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


# Get all events
@app.get("/events", response_model=list[schemas.EventResponse])
def get_events(
    db: Session = Depends(get_db)
):
    return db.query(models.Event).all()


# -----------------------------
# TICKET CATEGORY APIs
# -----------------------------

# Create a ticket category
@app.post(
    "/ticket-categories",
    response_model=schemas.TicketCategoryResponse
)
def create_ticket_category(
    category: schemas.TicketCategoryCreate,
    db: Session = Depends(get_db)
):
    event = db.query(models.Event).filter(
        models.Event.id == category.event_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if category.price < 0 or category.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative and quantity must be positive"
        )

    new_category = models.TicketCategory(
        **category.model_dump()
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# Get all ticket categories
@app.get(
    "/ticket-categories",
    response_model=list[schemas.TicketCategoryResponse]
)
def get_ticket_categories(
    db: Session = Depends(get_db)
):
    return db.query(models.TicketCategory).all()



# -----------------------------
# BOOKING APIs
# -----------------------------

# Create a booking and send notification
@app.post("/bookings", response_model=schemas.BookingResponse)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db)
):
    try:
        new_booking = booking_agent.create_booking(
            db=db,
            user_id=booking.user_id,
            event_id=booking.event_id,
            ticket_category_id=booking.ticket_category_id,
            quantity=booking.quantity
        )

        event = db.query(models.Event).filter(
            models.Event.id == new_booking.event_id
        ).first()

        notification_agent.send_notification(
            db=db,
            user_id=new_booking.user_id,
            title="Booking Successful",
            message=(
                f"Your booking #{new_booking.id} for "
                f"{event.title} has been created successfully. "
                f"Quantity: {new_booking.quantity}."
            )
        )

        return new_booking

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )



# -----------------------------
# DIGITAL TICKET APIs
# -----------------------------

# Generate digital tickets for a booking
@app.post(
    "/bookings/{booking_id}/tickets",
    response_model=list[schemas.TicketResponse]
)
def generate_tickets(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    try:
        return ticket_agent.generate_tickets(
            db=db,
            booking_id=booking_id,
            quantity=booking.quantity
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# NEW: Get existing tickets for a booking
@app.get(
    "/bookings/{booking_id}/tickets",
    response_model=list[schemas.TicketResponse]
)
def get_booking_tickets(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return db.query(models.Ticket).filter(
        models.Ticket.booking_id == booking_id
    ).all()


# Check in an attendee using their ticket code
@app.post(
    "/tickets/{ticket_code}/check-in",
    response_model=schemas.TicketResponse
)
def check_in_ticket(
    ticket_code: str,
    db: Session = Depends(get_db)
):
    try:
        return ticket_agent.check_in_ticket(
            db=db,
            ticket_code=ticket_code
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# -----------------------------
# WAITLIST APIs
# -----------------------------

# Add an attendee message to the waitlist
@app.post(
    "/waitlist",
    response_model=schemas.WaitlistMessageResponse
)
def add_waitlist_message(
    message: schemas.WaitlistMessageCreate,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == message.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return waitlist_agent.add_to_waitlist(
        db=db,
        user_id=message.user_id,
        message_text=message.message_text
    )


# Get all waitlist messages
@app.get(
    "/waitlist",
    response_model=list[schemas.WaitlistMessageResponse]
)
def get_waitlist_messages(
    db: Session = Depends(get_db)
):
    return waitlist_agent.get_waitlist_messages(db)


# -----------------------------
# NOTIFICATION APIs
# -----------------------------

# Create a notification
@app.post(
    "/notifications",
    response_model=schemas.NotificationResponse
)
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == notification.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return notification_agent.send_notification(
        db=db,
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message
    )


# Get notifications for a user
@app.get(
    "/notifications/{user_id}",
    response_model=list[schemas.NotificationResponse]
)
def get_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    return notification_agent.get_user_notifications(
        db=db,
        user_id=user_id
    )


# Mark a notification as read
@app.put(
    "/notifications/{notification_id}/read",
    response_model=schemas.NotificationResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    try:
        return notification_agent.mark_as_read(
            db=db,
            notification_id=notification_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )
