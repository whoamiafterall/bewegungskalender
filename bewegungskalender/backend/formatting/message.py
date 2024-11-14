from bewegungskalender.backend.formatting.style import Style, style
from bewegungskalender.backend.io.cli import START, END
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.io.config import FOOTER
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.libs.datetime import weekday_date, event_time
from bewegungskalender.backend.formatting.format import add_link, escape, Format, match_and_add_recurring

class MultiFormatMessage:
    def __init__(self) -> None:
        self.start = START
        self.end = END
        self.html:str = ""
        self.markdown:str = ""
        self.txt:str = ""
        
    # set Format from a given String
    def get(self, frmt: str | Format) -> str:
        """Get the message of this instance in the specified frmt.

        Args:
            frmt (str|Format): The frmt to be used as a **string** or of type **Format**.

        Returns:
            str: The message formatted in the specified frmt.
        """    
        match frmt:
            case 'html' | Format.HTML:
                return self.html     
            case 'md' | Format.MD:
                return self.markdown
            case 'txt' | Format.TXT:
                return self.txt
            case _:
                LOGGER.warning(f"Format: {frmt} does not exist. Choose: 'html', 'md' or 'txt'.")
                exit(1) 
            
    def __str__(self) -> str:
        return f"Events from {self.start} to {self.end} in Txt Format: \n{self.txt}"
    
    def __repr__(self) -> str:
        return f"MultiFormatMessage:\nstart={self.start}\nend={self.end}\ntxt=\n{self.txt}"
    
    def newline(self):
        self.txt += Format.TXT.newline()
        self.markdown += Format.MD.newline()
        self.html += Format.HTML.newline()
        
    def header(self): # Displayed as Head of the Message => style info on the Timerange
        header = f"Die Termine vom " + weekday_date(self.start) + " - " + weekday_date(self.end)
        self.txt += header
        self.markdown += style(escape(header), Format.MD, Style.BOLD)
        self.html += style(header, Format.HTML, Style.BOLD)
   
    # Create Titles out of Calendar Names (Categories) and Emojis - adds style for HTML and Markdown.
    def calendar_title(self, emoji: str, name: str):
        self.txt += f"{emoji} {name}"
        self.markdown += style(f"{emoji} {escape(name)}", Format.MD, Style.BOLD)
        self.html += style(f"{emoji} {name}", Format.HTML, Style.BOLD)
        
    # This should be refactored at some point, but I'm happy that it properly works for now.
    def add_recurring_event(self, event: Event):
        self.txt = match_and_add_recurring(event, self.txt, Format.TXT)
        self.markdown = match_and_add_recurring(event, self.markdown, Format.MD)
        self.html = match_and_add_recurring(event, self.html, Format.HTML)

    def add_event(self, event:Event):
        self.txt += event_time(event.start, event.end) + add_link(event.summary, event.description, Format.TXT)
        self.markdown += escape(event_time(event.start, event.end)) + add_link(event.summary, event.description, Format.MD)
        self.html += event_time(event.start, event.end) + add_link(event.summary, event.description, Format.HTML)
        
    def footer(self):  # Displayed as End of the Message (List of links)
        footer_title:str =  "🌐 Weiterführende Links:"
        self.txt += footer_title
        self.markdown += style(escape(footer_title), Format.MD, Style.BOLD)
        self.html += style(escape(footer_title), Format.HTML, Style.BOLD)
        self.newline()
        for item in FOOTER:
            self.txt += f"{item['link']['text']}: {item['link']['url']}"
            self.markdown += add_link(escape(item['link']['text']), item['link']['url'], Format.MD)
            self.html += add_link(escape(item['link']['text']), item['link']['url'], Format.HTML)
            self.newline()

def create_message(data:list) -> MultiFormatMessage:
    message = MultiFormatMessage()
    message.header()
    message.newline()
    for calendar in data:
        LOGGER.debug(f"Formatting and adding {calendar.name} to message...")
        if calendar.events:
            message.newline()
            message.calendar_title(calendar.emoji, calendar.name) 
            message.newline()
            for event in calendar.events:
                if event.recurrence:
                    message.add_recurring_event(event)
                else:
                    message.add_event(event)
                    message.newline()
    message.newline()
    message.footer()
    LOGGER.info(f"Successfully formatted the message!")
    return message