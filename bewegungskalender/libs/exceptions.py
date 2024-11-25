# Custom Exception Classes

class NetworkConnectionError(Exception):
    """A Connection error occurred."""
    def __init__(self, url):
        super().__init__(f"\n\nCouldn't get data from {url} due to bad or no network connection.\n\n"
                                     f"Please check your network connection and rerun the program.")