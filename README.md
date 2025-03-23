# LG ProCentric EPG and Channel Bundle Creator

## Overview

This project is designed to model and format TV EPG (Electronic Program Guide) data for LG ProCentric servers. It fetches raw EPG data, processes it into a structured format, and ensures compatibility with the LG ProCentric server.

## Features

- Fetches and parses EPG data.
- Maps data to structured models (`Event`, `Channel`, `ProgramGuide`).
- Handles time zones, dates, and program durations.
- Safe extraction of data with default values for missing fields.

## Dependencies

- `requests`: For fetching data.
- `xml.etree.ElementTree`: For XML parsing.
- `pydantic`: For data modeling.
- `pytz`: For time zone handling.

## Current Sources

- New Zealand, SKY NZ GraphQL
- Australia, xmltv.net

## LG ProCentric Server

Preparing the data form importation is only the first step, you must host a Zip file on and accessable FTP server and has the file named correctly.

ZIP Naming Convention = Procentric_EPG_{ISO Country Code ie NZL}_{Date YYYYMMDD}.zip

JSON Naming Convention = Procentric_EPG.json

JSON payload needs to be enclosed into the the ZIP file and places in the approperate directory for collections over FTP.

### FTP Service
Your file needs to sit in a sub directory from a logged in FTP user.

Linux Users prospective
/home/procentric/EPG/NZL

FTP Users prospective
/EPG/NZL


### Expected JSON Format
```
{
    "filetype": "Pro:Centric JSON Program Guide Data NZL",
    "version": "0.1",
    "fetchTime": "2022-06-24T13:22:44+1200",
    "maxMinutes": 60,
    "channels": [
        {
            "channelID": "1",
            "name": "TVNZ One",
            "resolution": "HD",
            "events": [
                {
                    "eventID": "334242",
                    "title": "6 News",
                    "eventDescription": TVNZ New Zealand News",
                    "rating": "TV-MA",
                    "date": "2022-06-25",
                    "startTime": "1800",
                    "length": "60",
                    "genre": "News"
                }
            ]
        }
    ]
}
```
Good Luck.