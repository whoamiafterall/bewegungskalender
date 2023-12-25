from mastodon import Mastodon
from post_caldav_events.output.message import message

def login(config:dict):
    return Mastodon(
        client_id = config['mastodon']['client_key'],
        client_secret = config['mastodon']['client_secret'],
        access_token = config['mastodon']['access_token'],
        api_base_url= f"https://{config['mastodon']['instance']}/api/v1/apps"
    )