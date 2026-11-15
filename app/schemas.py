
from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Venue schemas
class VenueCreate(BaseModel):
    name: str
    location: str
    capacity: int
    description: str | None = None


class VenueResponse(BaseModel):
    id: int
    name: str
    location: str
    capacity: int
    description: str | None = None
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


# Venue hire request schemas
class VenueHireRequestCreate(BaseModel):
    user_id: int
    venue_id: int
    event_name: str
    requested_date: datetime
    expected_attendees: int


class VenueHireRequestResponse(BaseModel):
    id: int
    user_id: int
    venue_id: int
    event_name: str
    requested_date: datetime
    expected_attendees: int
    status: str

    model_config = ConfigDict(from_attributes=True)



# Event schemas
class EventCreate(BaseModel):
    title: str
    description: str | None = None
    event_date: datetime
    venue_id: int
    organizer_id: int


class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    event_date: datetime
    venue_id: int
    organizer_id: int
    status: str

    model_config = ConfigDict(from_attributes=True)



# Ticket Category schemas
class TicketCategoryCreate(BaseModel):
    name: str
    price: int
    quantity: int
    event_id: int


class TicketCategoryResponse(BaseModel):
    id: int
    name: str
    price: int
    quantity: int
    event_id: int

    model_config = ConfigDict(from_attributes=True)



# Booking schemas
class BookingCreate(BaseModel):
    user_id: int
    event_id: int
    ticket_category_id: int
    quantity: int


class BookingResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    ticket_category_id: int
    quantity: int
    total_price: int
    status: str

    model_config = ConfigDict(from_attributes=True)



# Ticket schemas
class TicketGenerateRequest(BaseModel):
    booking_id: int


class TicketResponse(BaseModel):
    id: int
    ticket_code: str
    booking_id: int
    is_checked_in: bool

    model_config = ConfigDict(from_attributes=True)



# Waitlist schemas
class WaitlistMessageCreate(BaseModel):
    user_id: int
    message_text: str


class WaitlistMessageResponse(BaseModel):
    id: int
    user_id: int
    message_text: str
    sender: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



# Notification schemas
class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
