from jinja2 import Environment, FileSystemLoader
from bewegungskalender.backend.io.config import TEMPLATING_DIR, MAP_POPUP_TEMPLATE

#start templating engine
environment = Environment(loader=FileSystemLoader(TEMPLATING_DIR))

#load templates
map_template = environment.get_template(MAP_POPUP_TEMPLATE)

def render_map_template(context):
    return map_template.render(context)
