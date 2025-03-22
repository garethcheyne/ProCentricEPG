import json
import os
import zipfile
from pathlib import Path
from models.epg_model import ProgramGuide  # Import your model

BASE_OUTPUT_DIR = Path("output")  # Base output directory

def save_json(data: ProgramGuide, subdirs: list[str]):
    """Save the program guide data as 'Procentric_EPG.json' inside subdirectories."""
    
    # Construct the full directory path
    output_path = BASE_OUTPUT_DIR.joinpath(*subdirs)
    output_path.mkdir(parents=True, exist_ok=True)  # Ensure directories exist
    
    json_path = output_path / "Procentric_EPG.json"  # Fixed filename
    
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data.dict(), f, indent=4)
    
    return json_path

def zip_json(json_path: Path, zip_filename: str):
    """Zip the JSON file with a custom ZIP filename and delete the original JSON file."""
    zip_path = json_path.parent / f"{zip_filename}.zip"  # Custom ZIP name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(json_path, json_path.name)

    # Delete the JSON file after zipping
    json_path.unlink()

    return zip_path


def save_and_zip(data: ProgramGuide, subdirs: list[str], zip_filename: str):
    """Save JSON as 'Procentric_EPG.json' and create a ZIP file with a custom name, then delete the JSON file."""
    json_path = save_json(data, subdirs)
    zip_path = zip_json(json_path, zip_filename)
    
    print(f"JSON saved: {json_path}")
    print(f"ZIP created: {zip_path}")
    print(f"JSON file deleted: {json_path}")

    return zip_path

