import logging
from models.epg_model import ProgramGuide
from utils.file_handler import save_and_zip
from epg_sources.xmltv_net.main import XMLTV
from epg_sources.sky_nz.main import SkyNZ_EPG


###############################
## For Australia
###############################
def create_xmltv_source(city: str, url: str, title: str):
    return XMLTV(url, title)

# List of Australian cities to process
cities = [
    {"city": "Sydney", "url": "https://xmltv.net/xml_files/Sydney.xml", "title": "Pro:Centric JSON Program Guide Data AUS Sydney"},
    {"city": "Brisbane", "url": "https://xmltv.net/xml_files/Brisbane.xml", "title": "Pro:Centric JSON Program Guide Data AUS Brisbane"},
    {"city": "Adelaide", "url": "https://xmltv.net/xml_files/Adelaide.xml", "title": "Pro:Centric JSON Program Guide Data AUS Adelaide"},
    {"city": "Goldcoast", "url": "https://xmltv.net/xml_files/Goldcoast.xml", "title": "Pro:Centric JSON Program Guide Data AUS Gold Coast"},
    {"city": "Melbourne", "url": "https://xmltv.net/xml_files/Melbourne.xml", "title": "Pro:Centric JSON Program Guide Data AUS Melbourne"}
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

# Process Australian cities
for city in cities:
    source = create_xmltv_source(city["city"], city["url"], city["title"])
    XMLTVProcess(source, ["EPG", "AU", city["city"]], f"Procentric_EPG_{city['city'][:3].upper()}")



###############################
## For New Zealand
###############################

epg = SkyNZ_EPG(url="https://api.skyone.co.nz/exp/graph", zip_output_path="./output/EPG/NZ/Procentric_EPG_NZL.zip")
logging.info(f"Fetching and parsing the XML data for New Zealand...")
data = epg.fetch_data()
if data:
    program_guide = epg.parse_program_data(data)
    if program_guide:
        save_and_zip(program_guide, ["EPG", "NZL"], 'Procentric_EPG_NZL')
    else:
        logging.warning(f"No program guide data found for New Zealand.")
