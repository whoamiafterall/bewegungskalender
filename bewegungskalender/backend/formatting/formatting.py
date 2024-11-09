import re
from bewegungskalender.backend.formatting.format import Format
from bewegungskalender.libs.datetime import date_str, event_time
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.libs.logger import LOGGER

# generic libs for handling different text formatting
def newline(frmt:Format) -> str:
    """Returns a newline statement depending on the Format "frmt". Useful to reuse when templating content.

    Args:
        frmt (Format): The format to be used.
    Returns:
        str: The newline statement in the specified format
    """
    match frmt:
        case Format.TXT:
            return "\n"
        case Format.MD:
            return "\n"
        case Format.HTML:
            return "\n<br>"

def escape(text:str, charset:str = "?_–*[]()~`>#+-=|.!'{''}''" ) -> str:
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

def add_link(summary:str, description:str, frmt:Format) -> str:
    if  description is not None:
        try: #
            url = re.search("(?P<url>https?://\S+)", description).group("url")
            match frmt:
                case Format.TXT:
                    return f" {summary}: {url}"
                case Format.MD:
                    return f" [{escape(summary)}]({url})"
                case Format.HTML:
                    return ' <a href=' + f"{url}" + '>' + f"{summary}"+ '</a>'
        except AttributeError:
            LOGGER.warning(f"L: {summary}: No Link in: {description}")
    return f" {escape(summary)}" if frmt is Format.MD else f" {summary}"

#Temporarily moved this here - should be reworked when introducing templating
def match_and_add_recurring(event: Event, message: str, frmt: Format) -> str:
    # Prepare regex, the primary entry of the event and the date to add if it's not the first occurrence
    regex = r'(\d{2}\.\d{2}\.\s)+(\(\d{2}\:\d{2}\)\:\s)?'
    match frmt: # change the regex depending on the format
        case Format.TXT:
            regex += f"({re.escape(event.summary)})"
        case Format.MD:
            regex = r'(\d{2}\\\.\d{2}\\\.\s)+(\\\(\d{2}\:\d{2}\\\)\:\s)?' + f"(\[{re.escape(escape(event.summary))}\])"
        case Format.HTML:
            regex += f"(.*{re.escape(event.summary)}<\/a>)"
        case _:
            LOGGER.exception(f"The Format {frmt} is not available."); exit(1)
    match = re.search(regex, message)  # Try to match the event in the existing message
    if match is None:  # If it's the first occurrence, add the whole entry of the event and return
        first_date = escape(event_time(event.start, event.end)) if frmt is Format.MD else event_time(event.start, event.end)
        return message + first_date + add_link(event.summary, event.description, frmt) + newline(frmt)
    else:  # If it's not the first occurrence add just the date and return
        date_to_add = escape(f"& {date_str(event.start)} ") if frmt is Format.MD else f"& {date_str(event.start)} "
        if match.group(2) is None: # If there is no start time add the date after the first date
            substitute = match.group(1) + date_to_add + match.group(3)
        else: # If there is a start time add the date between the first date and the start time
            substitute = match.group(1) + date_to_add + match.group(2) + match.group(3)
        return message[:match.span()[0]] + substitute + message[match.span()[1]:]
