
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
