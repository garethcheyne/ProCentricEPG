from pydantic import BaseModel
from typing import List
from datetime import datetime

class Event(BaseModel):
    eventID: str
    title: str
    eventDescription: str
    rating: str
    date: str  # Format: YYYY-MM-DD
    startTime: str  # Format: HHMM (24-hour time)
    length: str  # Duration in minutes
    genre: str

class Channel(BaseModel):
    channelID: str
    name: str
    resolution: str
    events: List[Event]

class ProgramGuide(BaseModel):
    filetype: str
    version: str
    fetchTime: str
    maxMinutes: int
    channels: List[Channel]

def get_fetch_time() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")