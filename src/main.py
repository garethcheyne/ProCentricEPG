from models.epg_model import ProgramGuide
from utils.file_handler import save_and_zip
from epg_sources.xmltv_net.main import XMLTV
from epg_sources.sky_nz.main import SkyNZ_EPG


# Create XMLTV objects for different Australian cities with a clear description
source_sydney = XMLTV("https://xmltv.net/xml_files/Sydney.xml", "Pro:Centric JSON Program Guide Data AUS Sydney")
source_brisbane = XMLTV("https://xmltv.net/xml_files/Brisbane.xml", "Pro:Centric JSON Program Guide Data AUS Brisbane")
source_adelaide = XMLTV("https://xmltv.net/xml_files/Adelaide.xml", "Pro:Centric JSON Program Guide Data AUS Adelaide")
source_goldcoast = XMLTV("https://xmltv.net/xml_files/Goldcoast.xml", "Pro:Centric JSON Program Guide Data AUS Gold Coast")

# Function to fetch and save EPG data for a given source
def XMLTVProcess(source: XMLTV, location_tags: list, file_prefix: str):
    try:
        # Fetch and parse the XML data into the ProgramGuide model
        
        print(f"Fetching and parsing the XML data for {source.title}...")
        
        program_guide = source.get_program_guide()
        print(f"Successfully fetched and parsed the XML data for {source.title}:")
        save_and_zip(program_guide, location_tags, file_prefix)
    except Exception as e:
        print(f"Error occurred while processing {source.title}: {e}")

# Fetch and save EPG data for Sydney, Brisbane, Adelaide, and Gold Coast
XMLTVProcess(source_sydney, ["EPG", "AU", "Sydney"], "Procentric_EPG_SYD")
XMLTVProcess(source_brisbane, ["EPG", "AU", "Brisbane"], "Procentric_EPG_BRN")
XMLTVProcess(source_adelaide, ["EPG", "AU", "Adelaide"], "Procentric_EPG_ADL")
XMLTVProcess(source_goldcoast, ["EPG", "AU", "GoldCoast"], "Procentric_EPG_GLD")



# Example Usage:
epg = SkyNZ_EPG(url="https://api.skyone.co.nz/exp/graph", zip_output_path="./output/EPG/NZ/Procentric_EPG_NZL.zip")
data = epg.fetch_data()
if data:
    program_guide = epg.parse_program_data(data)
    if program_guide:  
        save_and_zip(program_guide, ["EPG","NZ"], 'Procentric_EPG_NZL')