"""
from mastodon import Mastodon

from bewegungskalender.backend.formatting.message import create_message
from bewegungskalender.backend.io.credentials import MASTODON_CLIENT_KEY, MASTODON_CLIENT_SECRET, MASTODON_ACCESS_TOKEN, \
	MASTODON_INSTANCE


def login(config:dict):
    return Mastodon(
        client_id = MASTODON_CLIENT_KEY,
        client_secret = MASTODON_CLIENT_SECRET,
        access_token = MASTODON_ACCESS_TOKEN,
        api_base_url= f"https://{MASTODON_INSTANCE}/api/v1/apps"
    )
"""