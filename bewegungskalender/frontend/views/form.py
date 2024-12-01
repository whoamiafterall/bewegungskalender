# Create Form Page
from slugify import slugify

from bewegungskalender.backend.io.config import MENU
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.functions import loading, render_iframe
from bewegungskalender.frontend.navigation.router import ROUTER

@ROUTER.add(f"/{slugify(str(MENU['form']['label'].lower()))}/")
def form_view():
    loading(MENU['form']['label'])
    LOGGER.debug(f"Creating the Form using {MENU['form']['source']}.")
    render_iframe(MENU['form']['source'])