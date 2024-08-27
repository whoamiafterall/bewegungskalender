
# TODOs

## Nicegui

### Admin Panel

- [] create an admin panel for settings

### Map

- [] create a leaflet map out of mapData and display it in a nicegui Tab

### Calendar

- [] create a nice calendar-view
- [] or look for existing software
- [] could use calendar.HTMLCalendar
- [] could use fullcalendar.js

## switch to asyncio

- [] change all the relevant functions
- [] test

## Move Message to Class

- [X] define class (22.08.)
- [X] define classmethods
- [ ] fix recurring events

## Multilingual Support?

## Mastodon Support?

# Changelog

## WPForms (fixed 25.08.)

- [X] ValueError: time data '07/07/2024 - 19:M0' does not match format '%d/%m/%Y - %H:%M'  => L'isola Sommer Protest Fest Aachen
- [X] event.add('summary', f"{data[0]} ({data[3]})"); IndexError: list index out of range => Kino knirschendes Gold-Kies frisst Wald

## Nextcloud Forms (implemented 25.08.)

- [X] check how it is possible to support it
=> works, just use csv or ods file that is automatically updated and cron that on to the server, then search from last timestamp to now. Store timestamp.
- [X] check if web embedding is already shipped
- [X] implement
- [ ] ship

## Mail-Newsletter (fixed 22.08.)

- [x] fixed the SpamAssasin problem by properly creating a MimeMultiPart Message (txt and html)
- [ ] ship

## Auto-Update Telegram Message (Fixed 22.08.)

- [x] upgrade to python telegram bot 21.x.x
- [x] look for way to edit message in telegram Bot => see telegram .py
- [x] look for way to store message_ids => yaml file
- [x] added check if last message has changed or not, so it doesnt crash
- [x] add a cli-argument for editing
- [x] test
- [ ] send automatic updates to telegram message every day through cron => ship

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

# Shipped Changes (Last 02.04.)

- [x] upgrade dependencies locally
- [x] test
- [x] pip freeze > requirements.txt
- [x] pull stuff on server
- [x] renew .venv and install dependencies
- [x] copy config
- [x] test on server
