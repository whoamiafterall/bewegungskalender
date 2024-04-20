# Bewegungskalender2Telegram

This has been a fork of https://gitlab.com/iexos/caldav2telegram but can be seen as a standalone project by now.

## Features 
This script does several things (most of them optional) interacting with Nextcloud Calendars via caldav:
- Get Events submitted through a Form and automatically add them to a calendar
- Fetch all the Events from multiple Calendars in a given timeframe.
- Locate those Events on Openstreetmap using Nominatim, producing GeoJSON files for a [Map](https://umap.openstreetmap.fr/en/map/bewegungskalender-karte_1048275)
- Write a Message listing the Events in MarkDown, HTML, or Plain Text.
- Send the message to a Mailing List in HTML: bewegungskalender@lists.riseup.net
- Post the message to a Telegram channel in MarkDown: https://t.me/bewegungskalender
- Write the Message to StdOut in Plain Text

### Roadmap
- Add the Option to edit Telegram messages (in Progress)
- Add the Option to send the message to Mastodon
- Refactor to use more Object Oriented Programming
- Rewrite the Argparser to act like a cli-program with subcommands

See TODO.md for more information.

## Setup
This is a Work in Progress, it should be installable via `pip` in the future.

### Setup in Virtual Environment#

1) `python3 -m venv <directory>`
2) `source <directory>/bin/activate`
3) `cd <directory>`
4) `git clone https://github.com/whoamiafterall/bewegungskalender2telegram.git`
5) `pip install --upgrade pip`
6) `pip install -r requirements.txt` 

You need to create a config file. You can specify the path using `--config CONFIG_PATH` or use the default `config.yml`. 
Just copy `config.example.yml` and change it to your needs.

### Setup Telegram

For the telegram output, you will need to setup a telegram bot:

* get a token first, see the [Telegram documentation](https://core.telegram.org/bots#how-do-i-create-a-bot)
* insert the token into your config file
* invite the bot into a channel or group
* run with `--get-telegram-updates` flag to get the id of that channel/group
* you may get the update for being added to a channel only once! If you miss it, remove the bot from that channel and add it again
* insert the correct `channel_id` into your config file

## Running

Run the script via

```
cd bewegungskalender
python3 -m bewegungskalender.main
```
Use -h flag for more information

To make it post regular updates with Events, schedule it via cron or similar.

## Dev testing

This is a work in progress. You will need `pytest` and `podman-compose` to run tests.
