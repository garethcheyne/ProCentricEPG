import json
import logging
import os
from models.epg_model import ProgramGuide
from utils.file_handler import save_and_zip
from epg_sources.xmltv_net.main import XMLTV
from epg_sources.sky_nz.main import SkyNZ_EPG

# Ensure the 'debug' directory exists
debug_dir = './debug'
if not os.path.exists(debug_dir):
    os.makedirs(debug_dir)  # Create the directory if it doesn't exist

###############################
## For New Zealand
###############################

epg = SkyNZ_EPG(url="https://api.skyone.co.nz/exp/graph", zip_output_path="./output/EPG/NZ/Procentric_EPG_NZL.zip")
logging.info(f"Fetching and parsing the XML data for New Zealand...")
data = epg.fetch_data()

if data:
    # Check if the data is valid and write it to a file
    with open(os.path.join(debug_dir, "debug_skynz.json"), "w") as file:
    # Convert 'data' to a JSON-formatted string and write it to the file
        file.write(json.dumps(data, indent=4))  # Pretty print with an indent for readability

    program_guide = epg.parse_program_data(data)
    if program_guide:
        save_and_zip(program_guide, ["EPG", "NZL"], 'Procentric_EPG_NZL')
    else:
        logging.warning(f"No program guide data found for New Zealand.")



###############################
## For Australia
###############################
def create_xmltv_source(city: str, url: str, title: str, timezone_offset: int) -> XMLTV:
    return XMLTV(url, title, timezone_offset)

# List of Australian cities to process
cities = [
    {"city": "SYD", "url": "https://xmltv.net/xml_files/Sydney.xml", "title": "Pro:Centric JSON Program Guide Data AUS Sydney", "timezone": 11},  # AEDT
    {"city": "BNE", "url": "https://xmltv.net/xml_files/Brisbane.xml", "title": "Pro:Centric JSON Program Guide Data AUS Brisbane", "timezone": 10},  # AEST
    {"city": "ADL", "url": "https://xmltv.net/xml_files/Adelaide.xml", "title": "Pro:Centric JSON Program Guide Data AUS Adelaide", "timezone": 10.5},  # ACDT
    {"city": "OOL", "url": "https://xmltv.net/xml_files/Goldcoast.xml", "title": "Pro:Centric JSON Program Guide Data AUS Gold Coast", "timezone": 10},  # AEST
    {"city": "MEL", "url": "https://xmltv.net/xml_files/Melbourne.xml", "title": "Pro:Centric JSON Program Guide Data AUS Melbourne", "timezone": 11}  # AEDT
]

def XMLTVProcess(source: XMLTV, location_tags: list, file_prefix: str):
    try:
        logging.info(f"Fetching and parsing the XML data for '{source.title}'...")
        program_guide = source.get_program_guide()

        if program_guide:
            logging.info(f"Successfully fetched and parsed the XML data for '{source.title}'.")

            save_and_zip(program_guide, location_tags, file_prefix)
            logging.info(f"Data for '{source.title}' has been saved and zipped successfully.")
        else:
            logging.warning(f"No program guide data found for '{source.title}'.")

    except Exception as e:
        logging.error(f"Error occurred while processing '{source.title}': {e}")

# Ensure logging is configured
logging.basicConfig(level=logging.INFO)

# Process Australian cities
for city in cities:
    timezone_offset = 0 # city.get("timezone", 0)  # Default to 0 if not set
    source = create_xmltv_source(city["city"], city["url"], city["title"], timezone_offset)
    XMLTVProcess(source, ["EPG", "AUS", city["city"]], f"Procentric_EPG_{city['city']}")


