import pandas as pd
import websocket
import time
import os
import logging
import time
from datetime import datetime
from datetime import timedelta


def setup_logger(name, log_file):
    """To setup as many loggers as you want"""
    level = logging.INFO
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def full_stack():
    """
    log full error
    stack
    """
    import traceback
    import sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]  # remove call of full_stack, the printed exception
        # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
        stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr


def is_msk_open():
    """check if moscow stock exchange
    is open now or not.
    (Core Trading Session)
    """
    now = datetime.now()
    now = now.time()
    start = datetime.strptime('9:50:00', '%H:%M:%S').time()
    end = datetime.strptime('18:45:00', '%H:%M:%S').time()
    weekday = datetime.today().weekday()
    if weekday in [5, 6]:
        return False
    if now > start:
        if now < end:
            return True
    return False


def get_rub_bonds(tConnector):
    bonds = {}
    for key, value in tConnector.client.INIT_STRUCTURE['securities'].items():
        if (value['sectype'] == "BOND" or value['sectype'] == "GKO") and value['currency'] == 'RUR' and value['active'] == 'true':
            bonds[value['seccode']] = value
    return bonds


def mean_candle_price(candle):
    s = 0
    s += float(candle['open'])
    s += float(candle['close'])
    s += float(candle['high'])
    s += float(candle['low'])
    return round(s/4, 2)



def fetch_additional_info_bonds(bondsd, tConnector):
    res = {}
    errored = []
    counter = 0
    for seccode, data in bondsd.items():
        counter += 1
        #print(counter, end = '\r')
        try:
            fetched_info = tConnector.get_securities_info('1', seccode)
            for key, new_data in fetched_info.items():
                if key not in data:
                    data[key] = new_data
            if data['lotsize'] == "1":
                if seccode == data['isin']:
                    tConnector.client.tdata.clear_queue()
                    try:
                        mean_price = mean_candle_price(list(tConnector.get_history_data(seccode = seccode, count = 100, board = data['board'], period=5)['candles'].values())[-1])
                    except Exception:
                        mean_price = None
                        
                    data['last_price'] = (mean_price) 
                    res[seccode] = data
        except Exception as e:
            errored.append(seccode)
            #print(counter, len(res), seccode, e, end = '\r')
            time.sleep(1)
            pass
        #time.sleep(0.1)
        tConnector.client.tdata.clear_queue()
    return res


def bondinfo_to_df(bd_dict):
    df = {
        'seccode': [],
         'board': [],
         'last_price': [],
         'coupon_period': [],
         'shortname': [],
         'decimals': [],
         'minstep': [],
         'point_cost': [],
         'quotestype': [],
         'coupon_value': [],
         'facevalue': [],
         'accruedint': [],
         'isin': []
    }
    fields = list(df.keys())
    for key, value in bd_dict.items():
        for field in fields:
            try:
                df[field].append(float(value[field]))
            except:
                try:
                    df[field].append(value[field])
                except:
                    df[field].append(None)
    df =  pd.DataFrame(df)
    df['daily_interest'] = df['coupon_value'] / df['coupon_period'] /  df['facevalue']*1000
    return df


def get_bonds_df(tConnector, logger):
    '''returns a df with bonds info.
    Loads if from disk if there is a
    fresh enough file, if not - requests
    from transaq, returns and safe on the disk.
    '''
    request_data = False
    updated_f = '/var/data/bonds_info/last_updated'
    try:
         with open(updated_f) as f:
            line = f.readlines()[0].split('.')[0]
            last_updated = datetime.strptime(line, '%Y-%m-%d %H:%M:%S')
            if (last_updated + timedelta(hours=24)) < datetime.now():
                request_data = True
            if is_msk_open():
                # do not spend trading time, load at nignt
                request_data = False
    except FileNotFoundError:
        # but request data if absent
        request_data = True
    if request_data == False:
        try:
            data = pd.read_csv('/var/data/bonds_info/bonds_data.csv', index_col = [0])
            logger.info('bonds data loaded from file')
            return data
        except FileNotFoundError:
            request_data = True
    if request_data:
        bonds = get_rub_bonds(tConnector)
        logger.info('loading data from transaq server')
        full_bonds = fetch_additional_info_bonds(bonds, tConnector)
        data = bondinfo_to_df(full_bonds)
        data.to_csv('/var/data/bonds_info/bonds_data.csv')
        with open('/var/data/bonds_info/last_updated', 'w') as f:
            f.write(str(datetime.now()))
        logger.info('data loaded from transaq server')
        return data



class CachedApiReq:
    """
    a class to cache API requests
    """

    def __init__(self, client, cachtime, func, account_id):
        self.value = None
        self.cachtime = cachtime
        self.updated = None
        self.client = client
        self.func = func
        self.account_id = account_id

    def get(self):
        """
        return dict if exists. If if does not exests or outdated -
        request from api and return
        """
        outdated = False
        if self.updated is None:
            outdated = True
        elif self.updated + timedelta(seconds=self.cachtime) < datetime.now():
            outdated = True
        if outdated:
            self.value = self.func(self.client, self.account_id)
            self.updated = datetime.now()
        return self.value
    
    
    
def get_2hour_1m_candles(client, figi):
    """
    returns historical
    candles for last hour
    with 1m resolution
    """
    response = client.market_data.get_candles(figi=figi,
                                            from_=(datetime.now() - timedelta(hours=2)),
                                            to=datetime.now(), interval=1)
    return candles_to_dict(response)




class Cached2HourMeanPrices:
    """
    mean prices by last
    hour 1m candles. We won't buy
    if current price significantly higher
    then average.
    """

    def __init__(self, client, logger):
        self.data = {}
        self.logger = logger
        self.absent = []
        self.dump = True
        self.dumped = {}
        self.client = client

    def load_from_file(self, figi):
        try:
            with open('/var/data/mean_candles/{}.json'.format(figi)) as f:
                res = json.load(f)
                # print(res)
            # self.logger.info('%s json loaded', figi)
            self.data[figi] = {'updated': datetime.now(),
                               'prices': res}
        except Exception as e:
            if figi not in self.absent:
                self.absent.append(figi)
            self.data[figi] = {'updated': datetime.now(),
                               'prices': "NoCandles"}

    def calculate_mean_prices(self, candles, figi):
        """
        calculate mean prices
        by candles
        """
        try:
            opens = []
            closes = []
            highs = []
            lows = []
            for candle in candles.values():
                opens.append(candle['o'])
                closes.append(candle['c'])
                highs.append(candle['h'])
                lows.append(candle['l'])
            open_ = sum(opens) / len(opens)
            close = sum(closes) / len(closes)
            high = sum(highs) / len(highs)
            low = sum(lows) / len(lows)
            res = {'o': open_, 'c': close, 'h': high, 'l': low}
            if figi not in self.dumped:
                self.dumped[figi] = datetime.now()
            if self.dump and self.dumped[figi] + timedelta(seconds=300) < datetime.now():
                with open('/var/data/mean_candles/{}.json'.format(figi), 'w') as f:
                    json.dump(res, f)
                    self.dumped[figi] = datetime.now()
            return res
        except Exception:
            if figi in self.data:
                return self.data[figi]['prices']
            else:
                self.load_from_file(figi)
                return self.data[figi]['prices']

    def get(self, figi):
        if figi in self.absent:
            return self.data[figi]['prices']
        outdated = False
        if figi not in self.data:
            # self.logger.info('figi not in data')
            outdated = True
        elif self.data[figi]['updated'] + timedelta(seconds=250) < datetime.now():
            outdated = True
        if outdated:
            #self.logger.info('outdated')
            try:
                candles = get_2hour_1m_candles(self.client, figi)
                self.data[figi] = {'updated': datetime.now(),
                                   'prices': self.calculate_mean_prices(candles, figi)}
            except Exception:
                if figi in self.data:
                    self.data[figi]['updated'] = datetime.now()
                    return self.data[figi]['prices']
                else:
                    self.load_from_file(figi)
                    return self.data[figi]['prices']
        else:
            #self.logger.info('not outdated')
            pass
        return self.data[figi]['prices']
    
    

def select_bonds_by_price(prices, keep=0.85):
    """
    filter bonds
    by prices.
    keep with prices
    less then nominal
    and more then
    (nominal*keep)
    """
    keep = keep * 100
    res = []
    for figi, price in prices.items():
        if keep < price < 101:
            res.append(figi)
    return res