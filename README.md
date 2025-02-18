# Bewegungskalender2Telegram

This has been a fork of <https://gitlab.com/iexos/caldav2telegram> but can be seen as a standalone project by now.

## Features

This script does several things (most of them optional) interacting with Nextcloud Calendars via caldav:

- Get Events submitted through a Form and automatically add them to a calendar
- Fetch all the Events from multiple Calendars, locate those Events on Openstreetmap using Nominatim and store the information in a database
- Sync Changes regularly (through cron jobs) to keep the database up to date with the CalDav backend
- Display Events in a nice Web-App with a Map and List View with lots of filters
- Add an "About" Page to the Web-App
- Add a "Links" Page to the Web-App
- Write a Message listing the Events in MarkDown, HTML, or Plain Text.
- Send the message via Mail in HTML/Plaintext.
- Post the message to a Telegram channel in MarkDown
- Write the Message to StdOut in Plain Text

### Roadmap

- Form for submitting events to the Caldav backend
- Moderation tool for the caldav backend
- Api
- Automated Message to Signal
- Personalized newsletter
- Search feature

See TODO.md for more information.

## Setup

This is a Work in Progress, it should be installable via `pip` in the future.

### Setup in Virtual Environment

1) `git clone https://github.com/whoamiafterall/bewegungskalender2telegram.git <directory>`
2) `cd <directory>`
3) `python3.11 -m venv .venv` # Should be python3.10 or higher
4) `source <directory>/bin/activate`
5) `pip3 install --upgrade pip`
6) `pip install poetry`
7) `poetry install`
8) `nano config.yml` # Edit Config and change it to your needs
9) `cp credentials.example.yml credentials.yml && nano credentials.yml` # Copy Credentials file and add your credentials

### Setup Telegram

For the telegram output, you will need to setup a telegram bot:

- get a token first, see the [Telegram documentation](https://core.telegram.org/bots#how-do-i-create-a-bot)
- insert the token into your config file
- invite the bot into a channel or group
- run with `--get-telegram-updates` flag to get the id of that channel/group
- you may get the update for being added to a channel only once! If you miss it, remove the bot from that channel and add it again
- insert the correct `channel_id` into your config file

## Running

See the help information with this command:

``` cd bewegungskalender
    python3 -m bewegungskalender.main
```

You need to either run with -db full to fetch and store all events existing in your calendars, 
or -db search with -qe and -qs to search for events in a given timeframe (defaults to next 14 days)

To make it post regular updates with Events, schedule -n or -t via cron or similar.

There are plans to make this more comprehensible and easier with typer, but we're not there yet.