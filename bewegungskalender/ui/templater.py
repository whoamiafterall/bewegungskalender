from jinja2 import Environment, FileSystemLoader
from bewegungskalender.helper.config import config

#start templating engine
environment = Environment(loader=FileSystemLoader(config['templating_dir']))

#load templates
map_template = environment.get_template(config['map']['popup']['template'])

def render_map_template(context):
    return map_template.render(context)
