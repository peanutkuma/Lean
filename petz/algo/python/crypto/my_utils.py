import pandas as pd
import numpy as np

# the class is as follows
def mk_iterable(elem):
    try:
        _ = iter(elem)
        return elem
    except:
        return list([elem])

class MyRollingWindow():

    def __init__(self, period):
        self._df = pd.DataFrame()
        self._period = period
        pass
    
    def _append(self, df):
        idx = df.index 
        self._df = pd.concat([df, self._df]).reset_index().drop_duplicates().drop(idx.names, axis=1) 
        self._df.index = idx
    
    def level_size(self, level ):
        return self._df.groupby(level= level).size()
        
    def batch_update(self, df):
        """ update the underlying data frame in a batch"""
        self._append(df)
        self._df = self._df.groupby(level='symbol', as_index= False).apply(lambda x : x.sort_index(ascending=False).iloc[0:self._period])
        
        if len(self._df.index[0]) > 2:
            self._df.index = self._df.index.droplevel(0) # adjust the index
        self._df.sort_index(ascending=False, inplace=True)
    
    def update(self, time, data):
        """
        :param: time is the current time
        :param: data is a pandas dataframe with all the symbols and their different characterisitcs

        """
        time = mk_iterable(time)
        symbols = mk_iterable(data.index.values)
        multi_index = pd.MultiIndex.from_product([symbols, time], names= ['symbol','time'])
        df = pd.DataFrame(data.values, columns = data.columns, index = multi_index)
        self._append(df)
        self._df.groupby(level='symbol', as_index= False).apply(lambda x : x.sort_index(ascending=False).iloc[0:self._period])

        if len(self._df.index[0] ) > 2:
            self._df.index = self._df.index.droplevel(0) # adjust the index
        self._df.sort_index(ascending=False, inplace=True)

    def is_ready(self):
        """
        return true if all symbols have `self._period` numbers of entries historical data
        """
        return np.all(self._df.groupby(level='symbol').size() == self._period)

    def data(self):
        """
        just get a copy of the dataframe
        """
        return self._df

    def period(self):
        return self._period

    def returns(self, lag = 1 ):
        """
        calculate the pct change (also retunrs for price data) by the formula ( p(t) - p(t-lag))/ p(t-lag)
        :param: lag how many days ago to compare the returns

        """
        assert(self.is_ready())
        return self._df.groupby(level = 'symbol', as_index=False).pct_change(-lag).sort_index(ascending=False).dropna()
    
    def iterate(self, symbol, reverse = True):
        """
        iterate overa a particular symbol from newest entry to oldesd one 
        :param: symbol which symbol you would like to substet 
        :param: reverse whether to go from newest to oldest entry or backwards
        """
        asset = self._df.xs(symbol)

# helper (free) functions to compute the sigma and the momentum given an instance of a rollign window class

def mk_momentum(rolling_win, m=0, n=1):
    """
    Compute the momentum according to the formula:

    momentum(t)= (p(t-m)-p(t-n))/p(t-n)

    :param: rolling_win a rolling window object containing data indexed by ("symbol", "time") multi index
    :param: m offset of the first period to compute with (default = 0)
    :param: n offset of the second period to compute with (default = 1)

    """
    assert (m < n)
    res = rolling_win.returns(n).groupby(level='symbol', as_index=False).shift(-m).dropna()
    if res.index.nlevels > 2 :
        res.index = res.index.droplevel(level=0)
    return res

def mk_dataframe(symbols, time, bar):
    """
    transform a dictionary of bar data into pandas dataframe
    """
    df = pd.DataFrame(columns = ["close", "high" ,"low" ,"open", "volume"])
    for symbol in symbols:
        _ = bar[symbol]
        _ = pd.DataFrame({"close" : [_.Close], "high":[_.High],
                      "low":[_.Low], "open" :[_.Open], "volume" :[ _.Volume]})
        df = pd.concat([df,_], ignore_index = True)

    midx = pd.MultiIndex.from_product([symbols,[time]], names = ["symbol","time"])
    df.index = midx
    return df

def mk_sigma(data, window, level = "symbol"):
    """
    Compute the rolling std deviation over a window period 
    
    :param: rolling_win a rolling window object containing data indexed by ("symbol", "time") multi index
    :param: window the rolling window over which the sigma will be computed
    :param: level the level over which to group the index (default is "symbol")
    """
    assert(window < data.groupby(level=level).size().min())
    res =  data.groupby(level= level).rolling(window).std().shift(-window+1).dropna().sort_index(ascending=False)
    if res.index.nlevels > 2 :
        res.index = res.index.droplevel(level=0)
    return res

def mk_SMA(data, window, level = "symbol"):
    """
    Compute the rolling simple moving average over a window period 
    
    :param: rolling_win a rolling window object containing data indexed by ("symbol", "time") multi index
    :param: window the rolling window over which the sigma will be computed
    :param: level the level over which to group the index (default is "symbol")
    """
    assert(window < data.groupby(level=level).size().min())
    res = data.groupby(level= "symbol").rolling(window).mean().dropna()
    if res.index.nlevels > 2 :
        res.index = res.index.droplevel(level=0)
    return res

def mk_EMA(data, window, level = "symbol"):
    """
     Compute the rolling exponential moving average over a window period 
    
    :param: rolling_win a rolling window object containing data indexed by ("symbol", "time") multi index
    :param: window the rolling window over which the sigma will be computed
    :param: level the level over which to group the index (default is "symbol")
    """
    assert(window < data.groupby(level=level).size().min())
    res = data.ewm(span=window,adjust=False).mean().dropna()
    if res.index.nlevels > 2 :
        res.index = res.index.droplevel(level=0)
    return res


from scipy.signal import find_peaks

def mk_trendlines(data, stride, level = "symbol"):
    
    groups = data.groupby(level = level)
    assert(stride < data.groupby(level=level).size().max())
    
    trendlines = {}
    for nm, df in groups:
        if df.index.nlevels >= 2 :
            df.index = df.index.droplevel(level=0)
        nm = nm.split()[0]
        trendlines[nm] = []
        for i in range(0, len(df), stride):
            peaks, _  = find_peaks(df.values[i : i+stride])
            if len(peaks) > 0: 
                tbegin, tend = df.index[i+peaks[0]], df.index[i+peaks[-1]]
                begin, end = df.iloc[i+peaks[0]], df.iloc[i+peaks[-1]]
                trendlines[nm] = trendlines[nm]+ [(i+peaks[0], i+peaks[-1], tbegin, tend, begin,end)]
    return trendlines 

###################################################################################################
# Data acquisition modules
###################################################################################################
import os 
import enum 
import wget 
import datetime

class DataType(enum.Enum): 
    Quote = 1 
    Trade = 2
    
    
class DataStreamException(Exception):
    pass

class CryptoStream:
    
    # base url and supported markets
    url = "https://www.quantconnect.com/data/tree/crypto/{}/{}/{}"
    markets = ("gdax" ,"bitfinex" )
       
    def __init__(self, data_folder, debug = True):
        self.storage = data_folder
        self.debug = debug
    
    def format_tail(self, date, data_type ):
        dtype = "trade" if data_type == DataType.Trade else "quote"
        return "{}_{}.zip".format(date.strftime("%Y%m%d"), dtype)
    
    def download_one(self, path, ticker, market, resolution, date,  data_type = DataType.Trade): 
        """
        download zips directly from https://www.quantconnect.com/data/tree/crypto/gdax/minute/etheur/20170530_trade.zip
        https://www.quantconnect.com/data/tree/crypto/<market>/<resolution>/<ticker>/<YYYYMMDD>_<type>.zip
        """
        if market.lower() not in self.markets: 
            raise DataStreamException("Unknown market type {}".format(market))
        # now attempt download 
        dtype = "trade" if data_type == DataType.Trade else "quote"
        base_url = self.url.format(market.lower(), resolution.lower(), ticker.lower())
        src  = base_url + "/" + self.format_tail(date, data_type)
        dest = path 
        try: 
            if self.debug:
                print("downloading ")
            fname = wget.download(src,dest)
            os.chmod(fname,  0o666)
        except Exception:
            raise False
        return True
    
    def add_one(self, ticker, market, resolution, date, data_type = DataType.Trade):
        """
        add a single data file to the local data folder. Do nothing if file exists 
        :param: ticker the symbol name, e.g. "etheur"
        ... 
        
        """
        # first check if data exist 
        if market.lower() not in self.markets: 
            raise DataStreamException("Unknown market type {}".format(market))
        # check if file already exists 
        path = os.path.join(os.path.abspath(self.storage),"crypto",market.lower(),resolution.lower(), ticker.lower())
        download = False
        if not os.path.exists(path):
            if self.debug : 
                print ("directory base path '{}' does not exist".format(path))
            os.makedirs(path,exist_ok=True)
            download = True
        elif not os.path.exists(path + "/" + self.format_tail(date, data_type)):
            download = True
        else: 
            print  ("data already exists.")
        # if we need to download something        
        if download: 
            status = self.download_one(path, ticker, market, resolution, date,  data_type)
            if status == False: 
                raise DataStreamException("could not download {} {}-resolution data for {}".format(ticker, resolution, date))
    
    def add_many(self, ticker, market, resolution, begin, end , data_type = DataType.Trade):
        """
        add a multiple data files to the local data folder. Do nothing if files exist 
        :param: ticker the symbol name, e.g. "etheur"
        ... 
        
        """
        diff = end-begin
        for i in range(diff.days):
            date = (begin+datetime.timedelta(i))
            if self.debug: 
                print("adding data for {}.{} on {}".format(ticker, resolution, date.strftime("%Y%m%d")))
                      
            self.add_one(ticker, market,resolution, date, data_type)
            