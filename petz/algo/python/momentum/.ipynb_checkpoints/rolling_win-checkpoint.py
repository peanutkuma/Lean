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


