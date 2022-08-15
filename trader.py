from library import *

from transaq import TransaqConnector

from http.server import BaseHTTPRequestHandler, HTTPServer

import threading

import json

from datetime import datetime

messages_stats={'quatations': {'ok': 0, 'error': 0}}


def receive_quatations():


    def process_inst_data(inst_data):
        now = str(datetime.now())
        seccode = inst_data['seccode']
        if seccode not in quatations:
            quatations[seccode] = {}
        for key, value in inst_data.items():
            quatations[seccode][key] = [value, now]


    while True:
        try:
            update = None
            update = tConnector.client.sub.receive_data(timeout=60)
            if update is not None:
                update = update['quotations']['quotation']
                if type(update) is list:
                    for inst_data in update:
                        process_inst_data(inst_data)
                elif type(update) is dict:
                    process_inst_data(update)
                messages_stats['quatations']['ok']+=1
        except TimeoutError:
            pass
        except Exception as e:
            logger.error(update)
            logger.error(e)
            logger.error(full_stack())
            messages_stats['quatations']['error']+=1
            pass




class Server(BaseHTTPRequestHandler):
    """
    A HTTP server to expose latest
    price data and healthcheck
    """

    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        """wtf"""
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        """execute on get"""
        if self.path == '/prices':
            self._set_headers(200)
            self.wfile.write(json.dumps(quatations).encode('utf-8'))
        if self.path == '/messages_stats':
            self._set_headers(200)
            self.wfile.write(json.dumps(messages_stats).encode('utf-8'))



def run_http_server(server_class=HTTPServer, handler_class=Server, port=80):
    """run http server"""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print('Starting http on port %d...' % port)
    httpd.serve_forever()




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



quatations = {}



price_updater = threading.Thread(target=receive_quatations, args=())

price_updater.start()

webserver = threading.Thread(target=run_http_server, args=())

webserver.start()