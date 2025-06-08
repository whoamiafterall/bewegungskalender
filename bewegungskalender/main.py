# builtin imports
import asyncio
import locale
import sys
import time
from locale import setlocale

import icalendar
# external imports
from sqlmodel import select, desc

# internal imports
from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.client import get_calendar_by_url, get_all_events, get_upcoming_events
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.formatting.message import MultiFormatMessage, create_message
from bewegungskalender.backend.io.cli import FORMAT, ARGS, DB_MODE, DB_DUMP
from bewegungskalender.backend.io.config import CALENDARS, LOCALE
from bewegungskalender.backend.io.db import DB
from bewegungskalender.backend.io.nextcloud_forms import update_ncform
from bewegungskalender.backend.output.mail import send_mail
from bewegungskalender.backend.output.telegram_bot import get_telegram_updates, send_or_edit_telegram
from bewegungskalender.libs.logger import LOGGER

# external imports

# Set locale
LOGGER.debug(f"Args: {ARGS}")
LOGGER.debug('Setting locale...')
setlocale(locale.LC_ALL, LOCALE)

# Main Function if run as standalone program
def main():
	from bewegungskalender.frontend.main import start_ui
	# frontend.run can't be called from async call
	if ARGS.user_interface:
		LOGGER.info("Starting User Interface!")
		start_ui()
	else:
		asyncio.run(main_async())

# Main async function call if not running NiceGui
async def main_async():
	# Get Telegram Channel ID
	if ARGS.get_telegram_updates:
		LOGGER.info('Getting telegram channel id...')
		print(get_telegram_updates()); exit()
	
	# Input Section
	## Nextcloud Form Input
	if ARGS.update_ncform:
		update_ncform()

	# Update or Create Database
	db = DB()
	match DB_MODE:
		# Fetch all Events from Nextcloud and create a new database
		case 'full':
			db.drop_tables()
			db.create_tables()
			db.populate(get_all_events)
		case 'sync':
			## Sync Events using sync token stored in database
			db.update_events()
		case 'search':
			## Fetch Upcoming events in the Timeframe specified in Args
			db.drop_tables()
			db.create_tables()
			db.populate(get_upcoming_events)
	
	# Output Section
	## Dump Database
	if DB_DUMP:
		for event in [n.Event for n in db.dump()]:
			print(event.recurrence) # TODO Dump DB to Json File
	## Print Output
	if ARGS.print:
		## Create a Message in TXT, MD & HTML
		message: MultiFormatMessage = create_message(db)
		LOGGER.debug(f"Printing message in {FORMAT} Format: \n")
		print(message.get(FORMAT))
	## Mail Output
	if ARGS.send_mail:
		## Create a Message in TXT, MD & HTML
		message: MultiFormatMessage = create_message(db)
		LOGGER.info('Sending Message per Mail...')
		send_mail(message)
	## Send or Edit Telegram Message
	if ARGS.telegram:
		## Create a Message in TXT, MD & HTML
		message: MultiFormatMessage = create_message(db)
		await send_or_edit_telegram(message)
	
	LOGGER.info('Finished all Tasks - Quitting.\n')
	sys.exit(0)

# send mastodon newsletter #TODO Implement Mastodon
# if ARGS.send_mastodon:
#    mastodon = LOGin(config)
#    print(mastodon.me())
#    mastodon.toot(message(config, events, START, end, Format.MD))

# Run as Module or Standalone program
if __name__ in {"__main__", "__mp_main__"}:
	main()
