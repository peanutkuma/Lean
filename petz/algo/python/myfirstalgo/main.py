import pandas as pd

# PT imports
import numpy as np
import matplotlib.pylab as plt
from rolling_win import *

# some symbols from SP500
SPSOME= ["MMM", "ABT", "ABBV", "ABMD", "ACN", "ATVI", "ADBE", "AMD",
         "AAP", "AES", "AFL", "A", "APD", "AKAM", "ALK", "ALB", "ARE", "ALXN",
         "ALGN", "ALLE", "AGN", "ADS", "LNT", "ALL", "GOOGL", "GOOG"]

DIM = 21
DIY = 12*21

class UncoupledNadionProcessor(QCAlgorithm):

    lookback = 3*DIY
    window = None

    def Initialize(self):
        self.SetStartDate(2020, 7, 5)  # Set Start Date
        self.SetEndDate(2020,7,10) # set end data
        self.SetCash(100000)  # Set Strategy Cash

        self.symbols = []
        ## add daily resolution
        for ass in SPSOME:
            self.symbols = self.symbols + [self.AddEquity(ass, Resolution.Daily)]

        history = self.History(SPSOME, self.lookback, Resolution.Daily)
        self.window = MyRollingWindow(self.lookback)
        self.window.batch_update(history) # prepare data
        pass

    def mk_dataframe(self, symbols, time, bar):
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

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
        bars = data.Bars
        mydata = self.mk_dataframe(self.symbols, self.Time, data)
        self.window.update(self.Time, mydata)
