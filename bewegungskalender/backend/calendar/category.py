from bewegungskalender.backend.calendar.event import Event

# This is the Category Class used to categorize events
class Category:
    def __init__(self, name:str, events:list[Event], emoji, map_marker:str):
        self.name = name
        self.events = events
        self.emoji = emoji
        self.map_marker = map_marker
