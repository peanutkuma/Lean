import quantopian.algorithm as algo
import quantopian.optimize as opt


from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.data import morningstar
from quantopian.pipeline.filters import QTradableStocksUS, StaticSids, StaticAssets
from quantopian.pipeline.factors import CustomFactor, Returns, SimpleMovingAverage
    
from quantopian.pipeline.experimental import risk_loading_pipeline

import numpy as np 
import pandas as pd 

import copy 

import datetime
from sklearn import covariance
import scipy as sp
import cvxpy as cvx 


SP500= ["MMM", "ABT", "ABBV", "ABMD", "ACN", "ATVI", "ADBE", "AMD", "AAP", "AES", "AFL", "A", "APD", "AKAM", "ALK", "ALB", "ARE", "ALXN",
"ALGN", "ALLE", "AGN", "ADS", "LNT", "ALL", "GOOGL", "GOOG", "MO", "AMZN", "AMCR", "AEE", "AAL", "AEP", "AXP", "AIG", "AMT", "AWK",
"AMP", "ABC", "AME", "AMGN", "APH", "ADI", "ANSS", "ANTM", "AON", "AOS", "APA", "AIV", "AAPL", "AMAT", "APTV", "ADM", "ARNC", "ANET",
"AJG", "AIZ", "ATO", "T", "ADSK", "ADP", "AZO", "AVB", "AVY", "BKR", "BLL", "BAC", "BK", "BAX", "BDX", "BRK", "BBY", "BIIB", "BLK", "BA",
"BKNG", "BWA", "BXP", "BSX", "BMY", "AVGO", "BR", "BF", "CHRW", "COG", "CDNS", "CPB", "COF", "CPRI", "CAH", "KMX", "CCL", "CAT", "CBOE",
"CBRE", "CDW", "CE", "CNC", "CNP", "CTL", "CERN", "CF", "SCHW", "CHTR", "CVX", "CMG", "CB", "CHD", "CI", "XEC", "CINF", "CTAS", "CSCO",
"C", "CFG", "CTXS", "CLX", "CME", "CMS", "KO", "CTSH", "CL", "CMCSA", "CMA", "CAG", "CXO", "COP", "ED", "STZ", "COO", "CPRT", "GLW",
"CTVA", "COST", "COTY", "CCI", "CSX", "CMI", "CVS", "DHI", "DHR", "DRI", "DVA", "DE", "DAL", "XRAY", "DVN", "FANG", "DLR", "DFS",
"DISCA", "DISCK", "DISH", "DG", "DLTR", "D", "DOV", "DOW", "DTE", "DUK", "DRE", "DD", "DXC", "ETFC", "EMN", "ETN", "EBAY", "ECL", "EIX",
"EW", "EA", "EMR", "ETR", "EOG", "EFX", "EQIX", "EQR", "ESS", "EL", "EVRG", "ES", "RE", "EXC", "EXPE", "EXPD", "EXR", "XOM", "FFIV", "FB",
"FAST", "FRT", "FDX", "FIS", "FITB", "FE", "FRC", "FISV", "FLT", "FLIR", "FLS", "FMC", "F", "FTNT", "FTV", "FBHS", "FOXA", "FOX", "BEN",
"FCX", "GPS", "GRMN", "IT", "GD", "GE", "GIS", "GM", "GPC", "GILD", "GL", "GPN", "GS", "GWW", "HRB", "HAL", "HBI", "HOG", "HIG", "HAS",
"HCA", "PEAK", "HP", "HSIC", "HSY", "HES", "HPE", "HLT", "HFC", "HOLX", "HD", "HON", "HRL", "HST", "HPQ", "HUM", "HBAN", "HII", "IEX",
"IDXX", "INFO", "ITW", "ILMN", "IR", "INTC", "ICE", "IBM", "INCY", "IP", "IPG", "IFF", "INTU", "ISRG", "IVZ", "IPGP", "IQV", "IRM",
"JKHY", "J", "JBHT", "SJM", "JNJ", "JCI", "JPM", "JNPR", "KSU", "K", "KEY", "KEYS", "KMB", "KIM", "KMI", "KLAC", "KSS", "KHC", "KR", "LB",
"LHX", "LH", "LRCX", "LW", "LVS", "LEG", "LDOS", "LEN", "LLY", "LNC", "LIN", "LYV", "LKQ", "LMT", "L", "LOW", "LYB", "MTB", "M", "MRO",
"MPC", "MKTX", "MAR", "MMC", "MLM", "MAS", "MA", "MKC", "MXIM", "MCD", "MCK", "MDT", "MRK", "MET", "MTD", "MGM", "MCHP", "MU", "MSFT",
"MAA", "MHK", "TAP", "MDLZ", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "MYL", "NDAQ", "NOV", "NTAP", "NFLX", "NWL", "NEM", "NWSA",
"NWS", "NEE", "NLSN", "NKE", "NI", "NBL", "JWN", "NSC", "NTRS", "NOC", "NLOK", "NCLH", "NRG", "NUE", "NVDA", "NVR", "ORLY", "OXY",
"ODFL", "OMC", "OKE", "ORCL", "PCAR", "PKG", "PH", "PAYX", "PYPL", "PNR", "PBCT", "PEP", "PKI", "PRGO", "PFE", "PM", "PSX", "PNW", "PXD",
"PNC", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", "PSA", "PHM", "PVH", "QRVO", "PWR", "QCOM", "DGX", "RL", "RJF", "RTN", "O",
"REG", "REGN", "RF", "RSG", "RMD", "RHI", "ROK", "ROL", "ROP", "ROST", "RCL", "SPGI", "CRM", "SBAC", "SLB", "STX", "SEE", "SRE", "NOW",
"SHW", "SPG", "SWKS", "SLG", "SNA", "SO", "LUV", "SWK", "SBUX", "STT", "STE", "SYK", "SIVB", "SYF", "SNPS", "SYY", "TMUS", "TROW",
"TTWO", "TPR", "TGT", "TEL", "FTI", "TFX", "TXN", "TXT", "TMO", "TIF", "TJX", "TSCO", "TDG", "TRV", "TFC", "TWTR", "TSN", "UDR", "ULTA",
"USB", "UAA", "UA", "UNP", "UAL", "UNH", "UPS", "URI", "UTX", "UHS", "UNM", "VFC", "VLO", "VAR", "VTR", "VRSN", "VRSK", "VZ", "VRTX",
"VIAC", "V", "VNO", "VMC", "WRB", "WAB", "WMT", "WBA", "DIS", "WM", "WAT", "WEC", "WCG", "WFC", "WELL", "WDC", "WU", "WRK", "WY", "WHR",
"WMB", "WLTW", "WYNN", "XEL", "XRX", "XLNX", "XYL", "YUM", "ZBRA", "ZBH", "ZION", "ZTS"]


class PortfolioRecord():
    
    def __init__(self, context): 
        self.date = get_datetime() 
        self.pfolio = copy.copy(context.portfolio)

    def positions(self):
        return self.pfolio.positions
    
    def t_value(self):
        return self.pfolio.portfolio_value
    
    def p_value(self):
        return self.pfolio.positions_value
    
    def c_value(self):
        return self.pfolio.cash

class NQueue:
    
    def __init__(self, N=10, dtype = None):
        if N > 0:
            self.N = N
        else:
            self.N = 10
        self.items = []
        self.dtype = dtype
    
    def size(self): 
        return len(self.items)
    
    def pop(self):
        if len(self.items) > 0:
            return self.items.pop()
   
    def push(self,el):
        
        if self.dtype is not None: 
            assert type(el) == self.dtype, "{} is not of {} type".format(type(el), self.dtype)
            
        if(len(self.items) == self.N):
            self.pop()
            
        self.items.insert(0,el)
    
    def at(self,key):
        return self.items[key]
   


class TradeTape():

    # stores the latest and best achieving pfolio thus far
    # in a (asofdate, pfolio) tuple
    pfolio_max = None
  
    # stores the latest computed weights 
    weights = NQueue(N=10) 
    alphas = NQueue(N=10)
    pfolios = NQueue(N=10, dtype = PortfolioRecord)

    
    
#################################################################################################
# PeTz Helper functions and some global constants 
#################################################################################################

DIM = 21  # trading days in a month
DIQ= DIM*3 # trading days in a quarter
DIY = DIM*12 # trading days in year

def distance2friday(date):
    weekday = datetime.datetime.isoweekday(date)
    # distance to previous friday 
    if weekday >  5:
        return weekday - 5
    else: 
        return weekday + 2
####################################################### 
class Liquidity(CustomFactor):
    """  Liquidity factor """
    window_length = DIQ    
    inputs = [
               USEquityPricing.volume, # trading volume
               USEquityPricing.close, # closing prices
              ]
    # overload the compute method 
    def compute(self, today, assets, out, volume, prices):
        out[:] = np.nanmean(volume[-DIQ:])*prices[-distance2friday(today)]
        
####################################################### 
class Momentum(CustomFactor):
    """  Momentum factor """
    inputs = [USEquityPricing.close, # price
              Returns(window_length=126)]
    window_length = 252    
    # overload the compute method 
    def compute(self,today,assets,out,prices, returns):
        out[:] = ((prices[-DIM] - prices[-DIY])/prices[-DIY]
                  -(prices[-1] - prices[-DIM])/prices[-DIM]) 
#######################################################

#################################################################################################       
# Trading 
#################################################################################################
class MyAlgo(QCAlgorithm):
    
    def Initialize(self):
        """
        Called once at the start of the algorithm.
        """
        # every day X-minutes after market opens, calculate portfolio weights
        algo.schedule_function(
            calculate_portfolio, 
            algo.date_rules.every_day(),
            algo.time_rules.market_open(),
        )

        # every day X-minutes after market opens, 
        # decide if I shall trade or not  
        algo.schedule_function(
            evaluate_prospective_trade,  
            algo.date_rules.every_day(), 
            algo.time_rules.market_open(minutes = 60)
            )

        # every day after market closes, update the logs... 
        algo.schedule_function(
            update_tape, 
            algo.date_rules.every_day(), 
            algo.time_rules.market_close()
            )


        # Create our dynamic stock selector.
        algo.attach_pipeline(make_pipeline(), 'my_pipeline')
        algo.attach_pipeline(risk_loading_pipeline(), 'risk_factors') 

        self.tape = TradeTape() 
        self.trading = True

    def make_pipeline():
        """
        A function to create our dynamic stock selector pipeline containing

        i. the alpha factor, whatever that is 
        ii. the computed momentum 
        iii. the latest price 
        iv. the market cap of equity
        """

        MOM = Momentum()
        # EPS = morningstar.Fundamentals.basic_eps_earnings_reports.latest
        # alpha = (0.0*EPS.zscore() + 1.0*MOM.zscore())
        alpha = MOM 

        # Base universe set to the QTradableStocksUS    
        UNIV = StaticSids(SP500_sids) & QTradableStocksUS()
        # longs = alpha.top(200, mask = UNIV)
        # shorts = alpha.bottom(200, mask = UNIV) 

        # momentum based factor 
        pipe = Pipeline(
            columns={
                'alpha' : alpha,
                'momentum': MOM, 
                # 'price': USEquityPricing.latest,
                'mcap' :  morningstar.valuation.market_cap.latest
            },
            screen =  UNIV
         )
        return pipe


    ###############################################################################
    #     PORFOLIO Bookkeeping 
    ###############################################################################
    def before_trading_start(context, data):
        """ Called every day before market open.
        """
        context.output = algo.pipeline_output('my_pipeline')
        # store the latest alpha 
        context.tape.alphas.push((get_datetime(), context.output['momentum']))
        # These are the securities that we are interested in trading each day.
        context.risk_loadings = algo.pipeline_output('risk_factors')

    def update_tape(context, data):
        """ Record some log data from today: to be performed on EACH TRADING day, after market closes
        """
        if context.trading == False:  # if we are not trading, exit
            return 
        log.info("Updating tape on {}".format(get_datetime()))
        # store the last porfolio
        context.tape.pfolios.push(PortfolioRecord(context))
        # store the best performing portfolio thus far
        context.tape.pfolio_max = copy.copy(context.tape.pfolios.at(0))
        for idx in range(context.tape.pfolios.size()):
            if context.tape.pfolios.at(idx).p_value() > context.tape.pfolio_max.p_value(): 
                context.tape.pfolio_max = copy.copy(context.tape.pfolios.at(idx))
        log.info("N-days trailing Max pfolio on {}: {} ".format(context.tape.pfolio_max.date, 
                                                                        context.tape.pfolio_max.p_value()) )

    def decide_stop_trade(context, data): 
        """ if we have lost than x% of the maximum value achieved so far,
            set an abort flag: which shall close ALL positions until a more profitable time arives 
        """
        tape = context.tape
        if tape.pfolio_max is None or  np.abs(tape.pfolio_max.p_value()) == 0.0:
            return False

        # close positions if pfolio fell more than 5% of its max value and you did not incurr losses 2 consecutive times

        delta_max = (tape.pfolio_max.p_value() - tape.pfolios.at(0).p_value()) / np.abs(tape.pfolio_max.p_value())

        if tape.pfolios.size() >= 2:
            delta_latest  = (tape.pfolios.at(0).p_value() - tape.pfolios.at(1).p_value()) / tape.pfolios.at(0).p_value()
        else:
            delta_latest = 1.0
        log.info("Portfolio deltamax = {}".format(delta_max))     
        log.info("Portfolio delta latest = {}".format(delta_latest))                                                                                     

        # pfolio dropeed more than 5% of max value and lost more than 5% of its recent value
        if delta_max > 0.05 and delta_latest < -0.05: 
            log.info("Suspending trade on {}".format(get_datetime()))
            return True
        return False

    def decide_start_trade(context, data): 
        """ If I had bought at time t-1 at price p0: would my position at time t have profitted?

            Price(t-1) is p0
            Price(t) is p1 
            shares = (w[i]*portfolio_value/p0[i]).as(int)
            VALUE = sum_i shares[i]*p1[i] 

            return True if this speculative VALUE > pfolio_maxval 
        """
        # otherwise -> I estimate earnings
        # get yday's weights
        weights = context.tape.weights.at(1)[1]
        assets = weights.index.values

        prcs = data.history(assets, fields = 'price', bar_count = 2, frequency = '1d' )
        shares = map(int, ( weights * context.portfolio.cash) / prcs.iloc[0]  )
        shares = list(shares)

        ### maybe pfolio traling mean criterion to detect 'upwards' movement in trend?
        ###
        VALUE_YDAY = np.sum(np.array(shares)*prcs.iloc[0]) # yesterday's value 
        VALUE_TDAY = np.sum(np.array(shares)*prcs.iloc[-1]) # today's value
        today = get_datetime()
        # reusme if today's value of the portfolio is 
        # x% larger than yesterday's 
        if VALUE_TDAY > 1.02*VALUE_YDAY:
            log.info("Resuming trade on {}".format(today))
            return True
        log.info("Trade suspension continues on {}".format(today))
        return False

    def evaluate_prospective_trade(context, data):
        """
            decide whether to proceede with or suspend trading
        """
        # force execution if first trade after suspension
        # must make a move
        # this means a switch of context.trading from false to true
        was_suspended = not context.trading 
        if not context.trading: 
            # if I am NOT trading, decide whether to start
            context.trading = decide_start_trade(context, data) 
        else: 
            # if I am trading, decide whether to stop
            context.trading = not decide_stop_trade(context, data)

        if context.trading:
            # forse execution if we first trade after suspension
            execute_position(context, data, was_suspended)
        else:
            close_position(context,data)



    ###############################################################################
    #     PORFOLIO OPTIMIZATION 
    ###############################################################################
    def execute_position(context, data, forced = False):
        """ execute calculated position

            trade is executed only if sufficient change in the alpha factor has been observed, or 
            if trade is `forced` by setting the param `forced` to true! 

        """
        weights = context.tape.weights.at(0)[1]
        assets = weights.index
        assets2trade = assets[:]

        # select only those assets whose alphas have changed more than 5% over the past 5 days
        if context.tape.alphas.size() >= 5:
            dalpha = (context.tape.alphas.at(0)[1] - context.tape.alphas.at(4)[1])/(context.tape.alphas.at(4)[1].abs())
            assets2trade = dalpha[ dalpha.abs() > 0.05].index

        # nothing to do if the assets to trade havent reached a critical limit of 20%
        if len(assets2trade) < 0.2 * len(assets) and not forced:
            log.info("inssufficient change in alpha: retaining position")
            return

        if not forced: 
            # take assets - assets2trade 
            assets2keep = [a for a in assets if a not in assets2trade] 
            pfolio_weights = context.portfolio.current_portfolio_weights

            weights2keep = pfolio_weights[assets2keep] 
            weights2trade = weights[assets2trade] 

            # 1. keep the old weights ot be the same proportion of the pfolio 
            # but this will change the norm of computed weights 
            # 2. recover the normalization by finding `scale` satisfying the eqn:
            #  weights2trade.abs().sum()*scale = weights.abs().sum()  - weights2keep.abs.sum()
            # ==>
            #  scale = (weights.abs().sum()-weights2keep.abs().sum())/weights2trade.abs().sum())
            scale = np.abs((weights.abs().sum()-weights2keep.abs().sum())/weights2trade.abs().sum())
            if scale > 0:
                weights[assets2trade] = weights2trade[assets2trade] / scale

        log.info("Executing trade on {} with weights from {}".format(get_datetime(), context.tape.weights.at(0)[0]))
        #latest weights are at the head of the list 
        objective = opt.TargetWeights(weights) 
        # Add the RiskModelExposure constraints
        # neutralize_risk_factors = opt.experimental.RiskModelExposure(
        #     risk_model_loadings=risk_loadings,
        #     version=0
        # )
        # Define the list of constraints
        constraints = []

        # constraints.append(neutralize_risk_factors)
        # place optimal order
        algo.order_optimal_portfolio(
            objective=objective,
            constraints=constraints
        )

    def close_position(context, data): 

        log.info("Clsoing position on {}".format(get_datetime()))

        holdings = context.portfolio.positions.keys()
        weights = pd.Series(data = np.zeros(len(holdings)), index = holdings)
        objective = opt.TargetWeights(weights)
        constraints = []

        algo.order_optimal_portfolio(
            objective=objective,
            constraints=constraints
        )

    def _mk_covmtx(today, assets, data):
        prcs = data.history(assets, fields = 'price', bar_count = 100, frequency = '1d')
        returns = prcs.pct_change().dropna()
        # what if I use the normal covariance mtx and NOT the ledoit Wolf one? 
        # 1. the calculaitons are MUCH faster as np.cov is much faster than ledoit_wolf 
        # 2. the backtests show much worse performance: larger drowdowns, lower & negative returns!!! 
        cov = covariance.ledoit_wolf(returns.values)[0]
        # cov = np.cov(returns.values.T) 
        return returns, cov

    def _mk_loss(x, alpha, cov):
        ## can be another form 
        return cvx.quad_form(x, cov) 

    def _mk_constraints(x, alpha, cov, gain): 
        ## posititve returns of 15%
        N = cov.shape[0]
        _1 = np.ones((N,1))
        # make_profit = [x.T*alpha >= gain]
        make_profit = [] # better to include x.*
        ## postition concentration of at most 5% in both longs and shorts 
        dollar_neutral = [x <= 0.05 , x >= -0.05]
        ## well invested: 0.8 <= sum(|x_i|) <= 1.0
        aux_x = cvx.Variable(N)
        well_invested = [aux_x.T*_1 >= 0.8 , aux_x.T*_1 <= 1.0, aux_x >= x , aux_x >= -x] 
        ## make a bet in at least 70% of the assets 
        ## sum( (np.abs(x) > 1e-5).as(int) ) / N >= .7 <--- how to encode as a convex constraint?!
        diverse  = []
        ## net dollar exposure: | |longs| - |shorts| | shall be <= 0.1
        limited_exposure = [x.T*_1 <= 0.1, x.T*_1 >= -0.1]
        return make_profit + dollar_neutral + well_invested + diverse + limited_exposure

    def _mk_opt(N, alpha, covmtx, context, data):
        x = cvx.Variable(N, 1, name = 'x')
        loss = _mk_loss(x, alpha, covmtx)    
        constraints = _mk_constraints(x, alpha.values, covmtx, context.gain)
        problem = cvx.Problem(cvx.Minimize(loss-x.T*alpha.values), constraints)
        return problem

    def optimize(today, assets, context, data):
        returns, covmtx = _mk_covmtx(today, assets, data) 
        T, N = returns.shape
        Z = np.random.multivariate_normal(np.zeros(N,), covmtx)
        ### make other alpha here?
        ### ? OLS alpha versus returns?! # draw the dice 
        alpha = context.tape.alphas.at(0)[1][assets] + 0.01*Z 

        value = np.inf
        while np.isinf(value) and context.gain >= 0.0:
            problem = _mk_opt(N, alpha, covmtx, context, data)
            value = problem.solve()
            if np.isinf(value): 
                context.gain = context.gain - 0.02
        return problem , covmtx


    def calculate_portfolio(context, data): 
        """    
        calculate portfolio using quantopian's optimization api
        adapted from https://www.quantopian.com/lectures/example-long-short-equity-algorithm
        """
        # Retrieve pipeline output
        pipeline_data = context.output.dropna()
        risk_loadings = context.risk_loadings
        # get asset names 
        assets = pipeline_data.index.values

        log.info("Universe size {}" . format(len(assets)))
        # get today's date 
        today = get_datetime()
        ### define the optimization problem 
        context.gain = 1.0 # maybe increase this to 2.0 ?!
        solution, covmtx = optimize(today, assets, context, data)
        value = solution.objective.value 

        weights = None 

        if value == None or np.isinf(value):
            log.info("Could not find a profitable pfolio! Closing ALL positions!")
            # or should I close? 
            weights = np.zeros( len(assets) )
        else:
            log.info("Gain optimized for is {}".format(context.gain))
            for var in solution.variables(): 
                if var.name() == 'x': 
                    weights = np.squeeze(np.asarray(var.value))
                    break 
                
        log.info("Solution vector size {}" . format(len(weights[np.abs(weights)> 0.0])))

        weights = pd.Series(weights, index = assets)
        # store the latest weights
        context.tape.weights.push((today, weights, covmtx))