import json
import os
import re
import zipfile
import requests
from typing import List
from datetime import datetime
from models.epg_model import ProgramGuide, Channel, Event, get_fetch_time

class SkyNZ_EPG:
    def __init__(self, url: str, zip_output_path: str):
        self.url = url
        self.zip_output_path = zip_output_path

    def fetch_data(self):
        """Fetch data from the GraphQL endpoint."""
        headers = {
            'Content-Type': 'application/json',
        }
        
        body = """
        {
            "query": "query getChannelGroup($id: ID!, $date: LocalDate) { experience(appId: TV_GUIDE_WEB) { channelGroup(id: $id) { id title channels { ... on LinearChannel { id title number tileImage { uri __typename } slotsForDay(date: $date) { slots { id startMs endMs live programme { ... on Episode { id title synopsis show { id title type __typename } __typename } ... on Movie { id title synopsis __typename } ... on PayPerViewEventProgram { id title synopsis __typename } } __typename } } __typename } } __typename } __typename } }",
            "variables": {
                "id": "4b7LA20J4iHaThwky9iVqn",
                "date": "2025-03-24"
            }
        }
        """
        
        response = requests.post(self.url, headers=headers, data=body)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print(f"Error: Failed to fetch data. Status code: {response.status_code}")
            return None

    def clean_string(self, input_string: str) -> str:
        """Removes unsupported characters and replaces them with a standard character."""
        # Remove non-ASCII characters
        cleaned_string = re.sub(r'[^\x00-\x7F]+', '', input_string)
        # Replace specific characters with standard ones (e.g., \u2019 -> regular apostrophe)
        cleaned_string = cleaned_string.replace('\u2019', "'")
        # You can add more replacements here if necessary (e.g., \u2026 -> ...)
        return cleaned_string

    def safe_find_text(self, parent, tag: str, default: str = "") -> str:
        """Safely finds the value of a dictionary key or returns a default value if the key is missing, and cleans the text."""
        if isinstance(parent, dict):
            # Get the value from the dictionary, ensuring it's a string
            value = str(parent.get(tag, default))
            # Clean the string before returning
            return self.clean_string(value)

        # If parent isn't a dictionary, return the default value cleaned
        return self.clean_string(str(default))

    def parse_program_data(self, data):
        """Parse the response data from the GraphQL query and map it to the ProgramGuide model."""
        # Ensure we have the expected structure
        if 'data' not in data or 'experience' not in data['data'] or 'channelGroup' not in data['data']['experience']:
            print("Error: Unexpected data structure.")
            return None

        # Prepare the ProgramGuide model
        program_guide = ProgramGuide(
            filetype="Pro:Centric JSON Program Guide Data NZL",
            version="1.0",
            fetchTime=get_fetch_time(),
            maxMinutes=0, 
            channels=[]
        )

        # Extract channel group and channels
        channel_group_data = data['data']['experience']['channelGroup']

        # Parse the channels
        for channel in channel_group_data['channels']:
            # Initialize Channel model
            channel_obj = Channel(
                channelID=channel['id'],
                name=channel['title'],
                resolution="HD",  # Default resolution, you might have to adjust if info is available
                events=[]
            )

            # Check if 'slotsForDay' exists and is a dictionary with the 'slots' key
            slots_for_day = channel.get('slotsForDay', {})
            if isinstance(slots_for_day, dict) and 'slots' in slots_for_day:
                for slot in slots_for_day['slots']:
                    # Map event data to the Event model

                    # Check if 'programme' and 'synopsis' exist before accessing
                    programme = slot.get('programme', {})
                    title = self.safe_find_text(programme, 'title', '')  # Safe retrieval
                    event_description = self.safe_find_text(programme, 'synopsis', '')  # Safe retrieval
                    


                    print(slot)

                # Map event data to the Event model
                    event_obj = Event(
                        eventID=slot['id'],
                        title=title,  # Default to empty string if title is missing
                        eventDescription=event_description,
                        rating="",  # If ratings are available, map them here
                        date=self.format_date(slot['startMs']),  # Ensure correct date format
                        startTime=self.format_start_time(slot['startMs']),  # Convert start time from ms
                        length=self.calculate_length(slot['startMs'], slot['endMs']),  # Duration in minutes
                        genre= self.extract_genre(programme)  # If genre is available
                    )

                    # Add the event to the channel's event list
                    channel_obj.events.append(event_obj)
            else:
                # Log a more detailed warning if 'slotsForDay' is not in the expected format
                print(f"Warning: 'slotsForDay' is not a valid list or missing for channel: {channel['title']}")
            
            # Add the channel to the ProgramGuide's channel list
            program_guide.channels.append(channel_obj)
            
        program_guide.maxMinutes = self.get_max_minutes(program_guide.channels)

        return program_guide

    def get_max_minutes(self, channels) -> int:
        """Calculate the total minutes from event.length in all channels."""
        max_minutes = 0
        for channel in channels:
            for event in channel.events:
                # Ensure the event length is valid before adding it to max_minutes
                try:
                    max_minutes += int(event.length)  # Sum up the length of all events
                except (ValueError, TypeError):
                    # If length is not a valid integer, treat it as 0
                    print(f"Warning: Invalid length for event {event.eventID}. Treating as 0 minutes.")
        return max_minutes


    def format_start_time(self, start_ms: int) -> str:
        """Convert start time in milliseconds to HHMM (24-hour format)."""
        start_time = datetime.utcfromtimestamp(start_ms / 1000)  # Convert ms to seconds
        return start_time.strftime("%H%M")

    def calculate_length(self, start_ms: int, end_ms: int) -> str:
        """Calculate the duration in minutes."""
        duration = (end_ms - start_ms) / 60000  # Convert milliseconds to minutes
        return str(int(duration))

    def extract_genre(self, programme) -> str:
        """Extract the genre of the programme (if available)."""
        # You may have to modify this depending on how the genre is represented in the programme data
        return programme.get('genre', '')

    def format_date(self, timestamp_ms):
        """Convert a timestamp in milliseconds to a human-readable date format (YYYY-MM-DD)."""
        # Convert milliseconds to seconds
        timestamp_sec = timestamp_ms / 1000.0
        # Create a datetime object from the timestamp
        dt = datetime.utcfromtimestamp(timestamp_sec)
        # Return the formatted date as a string (e.g., '2023-03-23')
        return dt.strftime('%Y-%m-%d')


