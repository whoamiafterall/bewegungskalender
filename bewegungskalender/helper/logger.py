from logging import getLogger, Logger, DEBUG, INFO, ERROR
from bewegungskalender.helper.cli import LOGLEVEL

# Return Logger and set log level
def get_logger() -> Logger:
    """Creates an instance of Class **Logger** from **logging** module and sets the **name** and **LOGLEVEL** according to the parameters. <br>

    Params:
        Name:
            name (str): The name to be used for the **Logger** instance.

    Returns:
        Logger: The **Logger** instance with the specified **Name** and **Loglevel**. 
    """        
    
    LOG =  getLogger(__name__)
    if LOGLEVEL != None:
        if LOGLEVEL == 'debug':
            LOG.setLevel(DEBUG)
        elif LOGLEVEL == 'info':
            LOG.setLevel(INFO)
        elif LOGLEVEL == 'error':
            LOG.setLevel(ERROR)
    return LOG

LOG = get_logger()