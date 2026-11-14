
from fastapi import FastAPI
from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EventSphere",
    description="Multi-Agent Venue Booking and Digital Ticketing Platform",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to EventSphere!"
    }

@app.get("/status")
def status():
    return {
        "status": "Running"
    }
