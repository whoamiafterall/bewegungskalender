from typing import Final

from bewegungskalender.backend.io.config import CALENDARS
from bewegungskalender.backend.io.credentials import NC_DOMAIN

# This File forges all relevant Links related to Nextcloud

# Used for exchanging data through caldav
NC_CALDAV_URL:Final[str] = f"https://{NC_DOMAIN}/remote.php/dav/calendars"

# Get Public Ids from Calendars as a single string
PUBLIC_IDS:Final[str] = ''.join(f"{line['calendar']['public']}-" for line in CALENDARS).rstrip('-')

# Nextclouds Base Urls:
_view_base_url:str = f"https://{NC_DOMAIN}/apps/calendar/p" # Base string for Views
_embed_base_url:str = f"https://{NC_DOMAIN}/apps/calendar/embed" # Base string for Embeds
_ics_base_url:str = f"https://{NC_DOMAIN}/public-calendars" # Base string for ics exports

def get_ics_url(public_id:str):
	return f"{_ics_base_url}/{public_id}?export"

# Nextcloud Toggle Parameters
_MONTHLY:Final[str] = "dayGridMonth"
_YEARLY:Final[str] = "multiMonthYear"
_LIST:Final[str] = "listMonth"

# Public Nextcloud Views
NC_MONTHLY_VIEW:Final[str] = f"{_view_base_url}/{PUBLIC_IDS}/{_MONTHLY}/now"
NC_YEARLY_VIEW:Final[str] = f"{_view_base_url}/{PUBLIC_IDS}/{_YEARLY}/now"
NC_LIST_VIEW:Final[str] = f"{_view_base_url}/{PUBLIC_IDS}/{_LIST}/now"
print(NC_LIST_VIEW)

# Embed Link
NC_MONTHLY_EMBED:Final[str] = f"{_embed_base_url}/{PUBLIC_IDS}/{_YEARLY}/now"
NC_YEARLY_EMBED:Final[str] = f"{_embed_base_url}/{PUBLIC_IDS}/{_YEARLY}/now"

