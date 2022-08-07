from library import *

from transaq import TransaqConnector

password = os.environ["TRANSAQ_PASS"]
login = os.environ["TRANSAQ_LOGIN"]
adapter_address = os.environ["TRANSAQ_ADAPTER_ADDRESS"]

dirs_to_exists = ['/var/data/logs', '/var/data/bonds_info']


for d in dirs_to_exists:
    if not os.path.exists(d):
        os.makedirs(d)    

logs_path = '/var/data/logs/trader.log'
logger = setup_logger("logger1", logs_path)

logger.setLevel(logging.INFO)

logger.info("Initialisation")