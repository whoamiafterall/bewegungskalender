import re
from datetime import datetime, time
from enum import StrEnum
from typing import TYPE_CHECKING

from bewegungskalender.libs.logger import LOGGER

if TYPE_CHECKING:
    from bewegungskalender.backend.calendar.event import Event
# TODO Break functions into smaller pieces and move them into class
# TODO Think of a way to make enum types inherit from format

class Format(StrEnum):
    HTML = 'html'
    MD = 'markdown'
    TXT = 'txt'

    def newline(self) -> str:
        """Returns a newline statement depending on the Format. Useful to reuse when templating content.

        Returns:
            str: The newline statement in the specified format
        """
        match self:
            case self.TXT|self.MD:
                return "\n"
            case self.HTML:
                return "\n<br>"


def escape(text: str, charset: str = "?_–*[]()~`>#+-=|.!'{''}''") -> str:
    """Escapes characters from a given charset in a given string with `\\\`'. <br>
    The default charset escapes all relevant characters for **Markdown and HTML** formatting.

    Args:
        text (str): The text where characters should be escaped with `\\\`.
        charset (str): The characters to be escaped. Defaults to: "?_–*[]()~`>#+-=|.!'{''}''"

    Returns:
        str: The given text with the only change that the given characters are escaped with `\\\`.
    """
    if text is None:
        return ""
    # Add "\\" in front of each character in the charset and return
    translate_dict = {c: "\\" + c for c in charset}
    return text.translate(str.maketrans(translate_dict))

def add_link(summary: str, url: str, frmt: Format) -> str:
    if url is None:
        return f" {escape(summary)}" if frmt is Format.MD else f" {summary}"
    match frmt:
        case Format.TXT:
            return f" {summary}: {url}"
        case Format.MD:
            return f" [{escape(summary)}]({url})"
        case Format.HTML:
            return ' <a href=' + f"{url}" + '>' + f"{summary}" + '</a>'


# Temporarily moved this here - should be reworked when introducing templating
def match_and_add_recurring(event: "Event", message: str, frmt: Format) -> str:
    # Prepare regex, the primary entry of the event and the date to add if it's not the first occurrence
    regex = r'(\d{2}\.\d{2}\.\s)+(\(\d{2}\:\d{2}\)\:\s)?'
    match frmt:  # change the regex depending on the format
        case Format.TXT:
            regex += f"({re.escape(event.summary)})"
        case Format.MD:
            regex = r'(\d{2}\\\.\d{2}\\\.\s)+(\\\(\d{2}\:\d{2}\\\)\:\s)?' + f"(\[{re.escape(escape(event.summary))}\])"
        case Format.HTML:
            regex += f"(.*{re.escape(event.summary)}<\/a>)"
        case _:
            LOGGER.exception(f"The Format {frmt} is not available.");
            exit(1)
    match = re.search(regex, message)  # Try to match the event in the existing message
    if match is None:  # If it's the first occurrence, add the whole entry of the event and return
        first_date = escape(event_time(event.start, event.end)) if frmt is Format.MD else event_time(event.start,
                                                                                                     event.end)
        return message + first_date + add_link(event.summary, event.description, frmt) + frmt.newline()
    else:  # If it's not the first occurrence add just the date and return
        date_to_add = escape(f"& {event.start:%d.%m.} ") if frmt is Format.MD else f"& {event.start:%d.%m.} "
        if match.group(2) is None:  # If there is no start time add the date after the first date
            substitute = match.group(1) + date_to_add + match.group(3)
        else:  # If there is a start time add the date between the first date and the start time
            substitute = match.group(1) + date_to_add + match.group(2) + match.group(3)
        return message[:match.span()[0]] + substitute + message[match.span()[1]:]


def event_time(start: datetime, end: datetime) -> str:
    if start.time() == time.min and start.date() != end.date():
        return f"{start:%d.%m.} - {end:%d.%m.}"
    elif start.time() == time.min and start.date() == end.date():
        return f"{start:%d.%m.}:"
    return f"{start:%d.%m.} {start:(%H:%M)}:"
