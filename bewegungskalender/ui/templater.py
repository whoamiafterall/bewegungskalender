from jinja2 import Environment, FileSystemLoader
from bewegungskalender.functions.config import CONFIG

#start templating engine
environment = Environment(loader=FileSystemLoader(CONFIG['templating_dir']))

#load templates
map_template = environment.get_template(CONFIG['map']['popup-template'])

def render_map_template(context):
    return map_template.render(context)
