# Create Form Page
from slugify import slugify

from bewegungskalender.backend.io.config import MAIN_MENU
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.functions import loading, render_iframe
from bewegungskalender.frontend.navigation.router import ROUTER

@ROUTER.add(slugify(f"/{str(MAIN_MENU['form']['label'].lower())}"))
def form_view():
    loading(MAIN_MENU['form']['label'])
    LOGGER.debug(f"Creating the Form using {MAIN_MENU['form']['source']}.")
    render_iframe(MAIN_MENU['form']['source'])