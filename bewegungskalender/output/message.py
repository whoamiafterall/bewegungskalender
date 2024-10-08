from datetime import date, datetime, time
import logging
from typing import Tuple
from bewegungskalender.helper.datetime import weekday_date
from bewegungskalender.helper.formatting import eventtime, match_and_add_recurring, md_link, escape_markdown, bold, Format

#TODO pass Message Object around to reduce clutter and get rid of the for loop

class MultiFormatMessage():
    def __init__(self, start:date, end:date) -> None:
        self.start = start
        self.end = end
        self.html:str = ""
        self.markdown:str = ""
        self.txt:str = ""
        
    def __str__(self) -> str:
        return f"Events from {self.start} to {self.end} in Txt Format: \n{self.txt}"
    
    def __repr__(self) -> str:
        return f"MultiFormatMessage:\nstart={self.start}\nend={self.end}\ntxt=\n{self.txt}"

    def newline(self):
        self.txt += "\n"
        self.markdown += "\n"
        self.html += "\n"
        
    def queryline(self) -> str: # Displayed as Head of the Message => bold info on the Timerange
        self.txt += (f"Die Termine vom " + weekday_date(self.start) + " - " + weekday_date(self.end))
        self.markdown += bold(escape_markdown((f"Die Termine vom " + weekday_date(self.start) + " - " + weekday_date(self.end))), Format.MD)
        self.html += bold(escape_markdown((f"Die Termine vom " + weekday_date(self.start) + " - " + weekday_date(self.end))), Format.HTML)
   
    # Create Titles out of Calendar Names (Categories) and Emojis - adds bold for HTML and Markdown.
    def calendar_title(self, emoji: str, name: str) -> str: 
        self.txt += f"{emoji} {name}"
        self.markdown += bold(f"{emoji} {escape_markdown(name)}", Format.MD)
        self.html += bold(f"{emoji} {escape_markdown(name)}", Format.HTML)
        
    # This should be refactored at some point, but i'm happy that it properly works for now.
    def add_recurring_event(self, event: Tuple) -> str:
        self.txt = match_and_add_recurring(event, self.txt, Format.TXT)
        self.markdown = match_and_add_recurring(event, self.markdown, Format.MD)
        self.html = match_and_add_recurring(event, self.html, Format.HTML)
     
    def add_event(self, event:Tuple):
        self.txt += eventtime(event.start, event.end) + f" {event.summary}"
        self.markdown += escape_markdown(eventtime(event.start, event.end)) + md_link(event.summary, event.description)
        self.html += escape_markdown(eventtime(event.start, event.end)) + md_link(event.summary, event.description)
        
    def footer(self, config:dict) -> str:  # Displayed as End of the Message (List of links)
        self.txt += "🌐 Weiterführende Links: \n"
        self.markdown += bold("🌐 Weiterführende Links: \n", Format.MD)
        self.html += bold("🌐 Weiterführende Links: \n", Format.HTML)
        for item in config['links']:
            self.txt += f"{item['link']['text']}: {item['link']['url']}\n"
            self.markdown += md_link(escape_markdown(item['link']['text']), item['link']['url']) + "\n"
            self.html += md_link(escape_markdown(item['link']['text']), item['link']['url']) + "\n"

def get_message(config:dict, data:list, start: date, stop: date) -> MultiFormatMessage:
    message = MultiFormatMessage(start, stop)
    message.queryline()
    message.newline()
    for calendar in data:
        logging.debug(f"Formatting and adding {calendar.name} to message...")
        if calendar.events != []:
            message.newline()
            message.calendar_title(calendar.emoji, calendar.name) 
            message.newline()
            for event in calendar.events:
                if event.recurrence is not None:
                    message.add_recurring_event(event)
                else:
                    message.add_event(event)
                    message.newline()
    message.newline()
    message.footer(config)
    logging.info(f"Successfully formatted the message!")
    return message