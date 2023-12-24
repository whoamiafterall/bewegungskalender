from enum import Enum
import re

class Format(Enum):
    HTML = 'html'
    MD = 'markdown'
    TXT = 'txt'

# generic functions for handling different text formatting

def newline():
    return "\n"

def bold(text:str, mode: Format) -> str:
    return "<b> " + text + " </b>" if mode == Format.HTML else ("*" + text + "*" if mode == Format.MD else text)

def italic(text:str, mode: Format) -> str:
    """
    Returns the given string in italic.
    
    Args:
        text (string): The string that shall be written in italic characters.
        mode (Format): The formatting mode to use.
    """    
    return "<i> " + text + " </i>" if mode == Format.HTML else ("_" + text + "_" if mode == Format.MD else text)
    
def markdownify(text:str) -> str:
    """
    escape characters to use markdown
    """
    if text is None:
        return ""
    escape_chars = "?_–*[]()~`>#+-=|.!'{''}''"
    translate_dict = {c: "\\" + c for c in escape_chars}
    return text.translate(str.maketrans(translate_dict))

def search_link(description:str) -> str:
    if  description is not None:
        try: return re.search("(?P<url>https?://[^\s]+)", description).group("url") 
        except AttributeError: return print(f"No Link found in:{description}")
    
def markdown_link(text:str, url:str) -> str:
    return f" [{markdownify(text)}]({search_link(url)})" if search_link(url) is not None else f" {text}"; print(f"No valid link in description of event:{text}")

def match_string(string:str, text:str, mode) -> str:
    regex = '\.\s.*'
    regex += re.escape(markdownify(f"{string}") if mode == Format.HTML or Format.MD else f"\..*{string}")
    return re.search(regex, text)