# Custom Exception Classes

class NetworkConnectionError(Exception):
    """A Connection error occurred."""
    def __init__(self, url):
        super().__init__(f"\n\nCouldn't get data from {url} due to bad or no network connection.\n\n"
                                     f"Please check your network connection and rerun the program.")

class NoLinkError(Exception):
    """No Link could be found,"""
    def __init__(self, string:str):
        super().__init__(f"No Link found in {string}")

class NoResultError(Exception):
    """No Result was found on this query."""
    def __init__(self, query:str):
        super().__init__(f"No Result found for {query}")