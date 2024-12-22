# Custom Exception Classes

class NoLinkError(Exception):
    """No Link could be found,"""
    def __init__(self, string:str):
        super().__init__(f"No Link found in {string}")

class NoResultError(Exception):
    """No Result was found on this query."""
    def __init__(self, query:str):
        super().__init__(f"No Result found for {query}")