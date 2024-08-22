
# TODOs

## WPForms

- Some Failures:
- [] ValueError: time data '07/07/2024 - 19:M0' does not match format '%d/%m/%Y - %H:%M'  => L'isola Sommer Protest Fest Aachen
- [] event.add('summary', f"{data[0]} ({data[3]})"); IndexError: list index out of range => Kino knirschendes Gold-Kies frisst Wald

## Nextcloud Forms

- [] check how it is possible to support it
- [] check if web embedding is already shipped

## Nicegui

### Admin Panel

- [] create an admin panel for settings

### Map

- [] create a leaflet map out of mapData and display it with nicegui

### Calendar

- [] maybe create a nice calendar-view too ?
- [] or look for existing software

## switch to asyncio

- [] change all the relevant functions
- [] test

## Move Message to Class

- [X] define class (22.08.)
- [] define classmethod which translates formats or pass the message around
- [] define constructor with: Format
- [] define methods

## Mastodon Support?

# Changelog

## Mail-Newsletter

- [x] fixed the SpamAssasin problem by properly creating a MimeMultiPart Message (txt and html)

## Auto-Update Telegram Message (Fixed 22.08.)

- [x] upgrade to python telegram bot 21.x.x
- [x] look for way to edit message in telegram Bot => see telegram .py
- [x] look for way to store message_ids => git repository
- [x] add a cli-argument for editing
- [x] test
- [x] send automatic updates to telegram message every day through cron

## Fix Map (Done 02.04.)

- [x] ~~look for way to host files via nextcloud~~ => nextcloud won't work - hosting them via git now
- [x] ~~search for webdav library~~ => using GitPython for now
- [x] ~~upload~~ => commit files automatically to new repository
- [x] add necessary entries to config files
- [x] change links in umap
- [x] test

## upgrade to calendar.search() (Done 02.04.)

- [x] upgrade date.search() to calendar.search()
- [x] test

## Shipped Changes (Last 02.04.)

- [x] upgrade dependencies locally
- [x] test
- [x] pip freeze > requirements.txt
- [x] pull stuff on server
- [x] renew .venv and install dependencies
- [x] copy config
- [x] test on server
