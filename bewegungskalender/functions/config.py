import yaml
from bewegungskalender.functions.cli import CONFIG_FILE
from bewegungskalender.functions.logger import LOGGER

# get Config from yml file
LOGGER.debug('Loading config file...')
try:
    with open(CONFIG_FILE, 'r') as f: 
        CONFIG:dict = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    LOGGER.exception('Config File not Found:', CONFIG_FILE); exit()
