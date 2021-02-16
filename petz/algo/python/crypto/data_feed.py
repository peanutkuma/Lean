import numpy as np 

import datetime
import pandas as pd
import psycopg2
import sqlalchemy
import getpass

RESOLUTION = {"1min": 60 , "5min" : 300, "15min" : 900, "1hr" : 3600, "6hr" : 21600, "1day" : 86400}

USER = "kenny"
DB_STRING = 'postgresql+psycopg2://{}:{}@localhost/finanz'

def connect2DB(user):
    pwd = getpass.getpass("Get password for {}".format(user))
    # and create a connection to posgresql or use sqlalchemy 
    db_engine = sqlalchemy.create_engine(DB_STRING.format(user,pwd), pool_recycle=3600)
    db_conn = db_engine.connect()
    return db_conn


class DataStream:
    
    data = None 
        
    def __init__(self, tickers,  begin, end, dt, resolution):
        self.tickers = tickers 
        self.begin = begin
        self.end = end 
        self.dt = dt # time increment interval 
        self.resolution = resolution
        self.conn = connect2DB(USER)
        self.symbols = pd.read_sql("select * from symbols where symbol IN ({}) ".format(",".join(["'{}'".format(t) for t in self.tickers])), self.conn )

        
    def __del__(self):
        # close the connection upon destruction
        self.conn.close()
    
    def __iter__(self):
        self.t0 = self.begin
        self.t1 = self.begin
        return self
    
    def __next__(self):
        # update pointers ... 
        self.t0 = self.t1 
        self.t1 = self.t0 + self.dt
        
        if self.t0 > self.end: 
            raise StopIteration
        # else ... 
        t0 = self.t0
        t1 = min(self.t1, self.end)
        df = pd.read_sql("select * from candles where fk_symbol in ({}) " 
                         "AND time >= '{}' AND time <'{}' and resolution_sec = {} ORDER BY time;".format(",".join([str(i) for i in self.symbols.id]),
                                                                                                            t0.strftime("%Y-%m-%d %H:%M:%S"), 
                                                                                                            t1.strftime("%Y-%m-%d %H:%M:%S"),self.resolution),
                                                                                                            self.conn)
        # if no new data skip ... 
        if df.empty: 
            return None 
        # else return the datapoints 
        columns = ['time','high','low','open','close','volume','resolution_sec', 'symbol','fk_symbol']
        df = df.merge(self.symbols, left_on = "fk_symbol", right_on = "id")[columns]
        df.set_index(["symbol","time"], inplace = True)
        return df  