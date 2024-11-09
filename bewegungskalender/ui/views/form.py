# Create Form Page
from slugify import slugify

from bewegungskalender.functions.config import MENU_ITEMS
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.ui.functions import loading, render_iframe
from bewegungskalender.ui.navigation.router import ROUTER

@ROUTER.add(slugify(f"/{str(MENU_ITEMS['form']['label'].lower())}"))
def form_view():
    loading(MENU_ITEMS['form']['label'])
    LOGGER.debug(f"Creating the Form using {MENU_ITEMS['form']['source']}.")
    render_iframe(MENU_ITEMS['form']['source'])