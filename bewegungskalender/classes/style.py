from enum import Enum
from bewegungskalender.classes.format import Format

class Style(Enum):
    BOLD = 'bold'
    ITALIC = 'italic'
    CODE = 'code'
    STRIKETHROUGH = 'strikethrough'
    UNDERLINE = 'underline'
    HIGHLIGHT = 'highlight'

def style(text: str, frmt: Format, st: Style) -> str | None:
    """Styles the given text in the given frmt with the given style.

    Args:
        text (str): The text to be styled.
        frmt (Format): The frmt to be used. See Format Class.
        st (Style): The style to be used. See Style Class.

    Returns:
        str: The styled **text** in the given frmt with the given style.
    """
    if frmt == Format.TXT:
        return
    match st:
        case Style.BOLD:
            return "<b> " + text + " </b>" if frmt == Format.HTML else ("*" + text + "*")
        case Style.ITALIC:
            return "<i> " + text + " </i>" if frmt == Format.HTML else ("_" + text + "_")
        case Style.CODE:
            return "<code> " + text + " </code>" if frmt == Format.HTML else ("`" + text + "`")
        case Style.STRIKETHROUGH:
            return "<s> " + text + " </s>" if frmt == Format.HTML else ("~~" + text + "~~")
        case Style.UNDERLINE:
            return "<u> " + text + " </u>"
        case Style.HIGHLIGHT:
            return "<mark> " + text + " </mark>" if frmt == Format.HTML else ("==" + text + "==")
