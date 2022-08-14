from library import *

from transaq import TransaqConnector



def receive_quatations():
    while True:
        try:
            update = tConnector.client.sub.receive_data(timeout=0.01)
            if update is not None:
                for inst_data in update.values():
                    seccode = inst_data['seccode']
                    if seccode not in quatations:
                        quatations[seccode] = {}
                    for key, value in inst_data.items():
                        quatations[seccode][key] = value
        except:
            pass



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


logger.info('loading tinkoff tickers')

tinkoff_tickers = []

with open('tinkoff_tickers.txt') as f:
    lines = f.readlines()
for line in lines:
    tinkoff_tickers.append(line[:-1])



logger.info('%s tinkoff tickers to exclude', len(tinkoff_tickers))

logger.info('connecting to transaq adapter')

tConnector = TransaqConnector(adapter_address)
tConnector.connect(login)


logger.info('Connection established')

logger.info('getting portfolio')

portfolio = get_portfolio(tConnector)

logger.info("%s bonds in portfolio", str(len(portfolio['positions'])))

logger.info ("getting bonds df")

bonds_df = get_bonds_df(tConnector, logger)

logger.info('bonds_df obtained')

logger.info('selecting bonds to buy')

selected_by_price, boards = select_bonds_by_price(bonds_df, except_list = tinkoff_tickers)

logger.info("%s bonds are selected to buy", str(len(selected_by_price)))

logger.info("subscribing on selected bonds quataions")


tConnector.subscribe(method = 'quotations', seccodes = selected_by_price,
                    boards = boards, callback = None)

logger.info('subscribed')

receive_quatations()