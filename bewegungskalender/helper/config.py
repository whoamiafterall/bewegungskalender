import logging
import yaml
from bewegungskalender.helper.cli import args

# get Config from yml file
logging.debug('Loading config file...')
try:
    with open(args.config_file, 'r') as f: 
        config:dict = yaml.load(f, Loader=yaml.FullLoader) 
except FileNotFoundError:
    logging.exception('Config File not Found:', args.config_file); exit()
