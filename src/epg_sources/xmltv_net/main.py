import random
import string
import requests
import pytz
import xml.etree.ElementTree as ET
from datetime import datetime
from models.epg_model import ProgramGuide, Channel, Event

class XMLTV:
    def __init__(self, url: str, title: str, timezone: int = 0):
        self.url = url
        self.title = title
        self.timezone = timezone

    def get_fetch_time(self) -> str:
        """Returns the current timestamp in the required format with timezone offset."""
        # Get the current time in the local timezone (you can adjust the timezone if needed)
        local_tz = pytz.timezone("Australia/Sydney")  # Adjust to your local timezone
        now = datetime.now(local_tz)

        # Format the datetime with the required format
        return now.strftime("%Y-%m-%dT%H:%M:%S%z")

    def fetch_xml_data(self) -> str:
        """Fetch XML data from the provided URL with headers."""
        print(f"Fetching XML data from {self.url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to retrieve XML data. Status code: {response.status_code}")

    def generate_random_string(self, length=6) -> str:
        """Generate a random string of the given length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def safe_find_text(self, parent, tag: str, default: str = "") -> str:
        """Safely finds the text of an element or returns a default value if the element is missing."""
        element = parent.find(tag)
        return element.text if element is not None else default

    def safe_find_rating_value(self, parent) -> str:
        """Safely finds the rating value in the <rating><value>...</value></rating> tag or returns an empty string."""
        if parent is None:
            return ""  # Return empty string if parent is None

        rating_elem = parent.find('rating')
        if rating_elem is not None:
            value_elem = rating_elem.find('value')
            if value_elem is not None:
                return value_elem.text or ""  # Return empty string if the text is None
        return ""  # Return empty string if rating or value is not found


    def parse_xml_to_model(self, xml_data: str) -> ProgramGuide:
        """Parse the XML data and map it to the ProgramGuide Pydantic model."""
        print(f"Parsing the XML data for {self.title}...")
        root = ET.fromstring(xml_data)

        # Extract channel information
        channels = []
        for channel_elem in root.findall('channel'):
            channel = Channel(
                channelID=channel_elem.get('id'),
                name=self.safe_find_text(channel_elem, 'display-name'),
                resolution="HD",  # Assume resolution is HD for now (update if needed)
                events=[]
            )

            # Extract program information
            for programme_elem in root.findall('programme'):
                # Extract and format the date
                if programme_elem.attrib['channel'] == channel_elem.get('id'):

                    start = programme_elem.get('start')  # Format: "YYYYMMDDHHMMSS Z"

                    # Convert start time to local timezone
                    utc_time = datetime.strptime(start, "%Y%m%d%H%M%S %z")  # Parse with timezone
                    local_tz = pytz.FixedOffset(self.timezone * 60)  # Convert minutes offset to tzinfo
                    local_time = utc_time.astimezone(local_tz)  # Convert to local time

                    formatted_date = local_time.strftime("%Y-%m-%d")  # Extract date
                    start_time = local_time.strftime("%H%M")  # Extract time in HH:MM format


                    event = Event(
                        eventID=self.generate_random_string(),
                        title=self.safe_find_text(programme_elem, 'title'),
                        eventDescription=self.safe_find_text(programme_elem, 'desc'),
                        rating=self.safe_find_rating_value(programme_elem),
                        date=formatted_date,
                        startTime=start_time,
                        length=str(int((datetime.strptime(programme_elem.get('stop'), "%Y%m%d%H%M%S %z") - utc_time).total_seconds() // 60)),
                        genre=self.safe_find_text(programme_elem, 'category')
                    )
                    channel.events.append(event)
            channels.append(channel)

        # Now calculate the maxMinutes by passing the ProgramGuide object
        program_guide = ProgramGuide(
            filetype=self.title,
            version="1.0",
            fetchTime=self.get_fetch_time(),
            maxMinutes=self.get_max_minutes(channels),  # Pass channels to the method
            channels=channels
        )
        
        return program_guide

    def get_max_minutes(self, channels) -> int:
        """Calculate the total minutes from event.length in all channels."""
        max_minutes = 0
        for channel in channels:
            for event in channel.events:
                max_minutes += int(event.length)  # Sum up the length of all events
        return max_minutes

    def get_program_guide(self) -> ProgramGuide:
        """Fetch the XML and parse it into the ProgramGuide model."""
        print(f"Get Program XML data for {self.title}...")
        xml_data = self.fetch_xml_data()
        return self.parse_xml_to_model(xml_data)
