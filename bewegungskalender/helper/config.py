import yaml
from bewegungskalender.helper.cli import CONFIG_FILE
from bewegungskalender.helper.logger import LOG

# get Config from yml file
LOG.debug('Loading config file...')
try:
    with open(CONFIG_FILE, 'r') as f: 
        CONFIG:dict = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    LOG.exception('Config File not Found:', CONFIG_FILE); exit()
