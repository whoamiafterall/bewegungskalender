import re

def get_link(string: str):
    try:
        return try_get_link(string)
    except (TypeError, AttributeError):
        return None
def try_get_link(string: str):
    return re.search("(?P<url>https?://\S+)", string).group('url')
