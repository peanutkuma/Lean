# Notes on the QuantConnnect python API

**MAIN API DOCUMENTATION CAN BE FOUND** [HERE](https://www.quantconnect.com/docs/home/home)

Bootcamp (buy and hold equities)
--------------------------------

* 'Initialize' function

* At the very start of your algorithm we call the `Initialize()` method to set up your strategy. It is important to set up the state of your algorithm here so it can be restarted easily. Basic structure of the algo is as follows

```python
class BootCampTask(QCAlgorithm): # important to derive from QCAlgorithm! 

    def Initialize(self):
  '''Initialise the data and resolution required, as well as the cash and start-end dates 
     for your algorithm. All algorithms must initialized.'''
 
        self.AddEquity("SPY", Resolution.Daily)
        # 1. Set Starting Cash 
        self.SetCash(25000)
  
    def OnData(self, data):
     '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
     data: Slice object keyed by symbol containing the stock data
     '''   
     pass

```

### Initializing Analysis Dates

The date range for your backtest is defined in your Initialize method. You can set this with fixed dates or a datetime object. These methods are called `self.SetStartDate()` and `self.SetEndDate()`

### Adding Data

The `self.AddEquity()` method is used for manually requesting assets. It takes a string ticker of the current asset name and the resolution. For more information see the [documentation](https://www.quantconnect.com/docs/algorithm-reference/initializing-algorithms#Initializing-Algorithms-Selecting-Asset-Data).

The AddEquity (and all other AddAsset methods) return a security object. This gives you a reference to the security object you can use later.

### Documentation on adding (subscribing to ) data

* Algorithms can manually subscribe to data for specific assets they need or use universes to choose groups of assets based on filtering criteria (e.g. all stocks with volumes greater than $10M/day). See more about Universes here.

* To manually subscribe to a specific asset you can call the `AddEquity()`, `AddForex()`, `AddCrypto()`, `AddCfd()` and `AddOption()` methods in your `Initialize()` method. There is no official limit to how much data you can ask for, but there are practical resource limitations.  

* QuantConnect supports international trading across multiple timezones and markets. The `Market` parameter is used to distinguish between the same tickers on different exchanges (e.g. FXCM and OANDA both offer EURUSD but have different rates).

* The resolution of the data available depends on the type of data. For Equities, Futures, Forex, and Crypto we provide Tick, Second, Minute, Hourly, and Daily resolution. For Options, we only have minute bar data. These are specified by the Resolution enum

* If there is a gap in the data (e.g. because there are no trades), by default the data is still pumped into your strategy on each time step. This behavior is called "fillForward" and defaults to true. You can disable this by setting fillForward to false.

* By default equity data in QuantConnect is Split and Dividend adjusted backwards in time to give smooth continuous prices. This allows easy use for indicators. Historical prices can look a little bit strange if you don't understand why it was done: e.g. instead of $10.23 the price might read $1.21216.  Some algorithms need raw or partially adjusted price data. You can control this with the SetDataNormalizationMode() method. The DataNormalizationMode enum has the values Adjusted (default), Raw, SplitAdjusted, and TotalReturn. When data is set to Raw mode the dividends are paid as cash into your algorithm, and the splits are directly applied to your holding quantity.

* If you have your own custom data you'd like to backtest against, check out the [custom data](https://www.quantconnect.com/docs/algorithm-reference/importing-custom-data) section.

### Accessing securities

Securities in your algorithm can be accessed via the `self.Securities[symbol]` dictionary. It looks up a security by its symbol object or ticker string. Using this accessor you can look up a security and alter its models or data normalization mode.

### Algorithm's `Portfolio` dictionary  

* Again, one referes to equities via their **ticker symbol**, e.g. 'SPY' or 'IBM' etc.

* The algorithm Portfolio dictionary also has helper properties for quick look ups of things like: `Invested`, `TotalUnrealizedProfit`, `TotalPortfolioValue`, `TotalMarginUsed`.  You can see more properties in the [documentation](https://www.quantconnect.com/docs/algorithm-reference/securities-and-portfolio).

* Individual asset holdings are held in your Portfolio property. This can be accessed via the self.Portfolio[symbol] dictionary. Entries in the Portfolio dictionary are SecurityHolding objects with many properties about your holdings, such as: Invested, Quantity, AveragePrice and UnrealizedProfit. e.g:

```python
class BootCampTask(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 6, 1)
        self.SetEndDate(2017, 6, 2)
        
        #1. Update the AddEquity command to request IBM data
        self.ibm = self.AddEquity("IBM", Resolution.Daily)
        
    def OnData(self, data):
        
        #2. Display the Quantity of IBM Shares You Own
        self.Debug("Number of IBM Shares: " + str(self.Portfolio["IBM"].Quantity))
```

### Placing orders

There are many ways to submit orders through LEAN but we're going to start with a MarketOrder. It can be used like this `self.MarketOrder("AAPL", 200)`. Market orders are filled immediately when the market is open. If you are using daily data, the order isn't processed until the next morning. Daily bars only arrive at your algorithm after the market has closed.

The average fill price (the price at which an order was filled) of your asset is available in the Portfolio class. You can access it like this: Portfolio["IBM"].AveragePrice. In backtesting this is a modelled price. In live trading this is taken from your brokerage fill event.

```py
class BootCampTask(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 6, 1)
        self.SetEndDate(2017, 6, 15)

        #1,2. Select IWM minute resolution data and set it to Raw normalization mode
        self.iwm = self.AddEquity("IWM", Resolution.Minute)
        self.iwm.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
    def OnData(self, data):
        self.MarketOrder("IWM", 100)
        self.Debug(self.Portfolio["IWM"].AveragePrice)
        #3. Place an order for 100 shares of IWM and print the average fill price
        #4. Debug the AveragePrice of IWM
```

Bootcamp (buy and hold FOREX)
--------------------------------

### Requesting forex data

You should request Forex data in your `Initialize()` method. The `AddForex` method takes a string pair name, `Resolution` enum, market-name, fillforward (default true) and leverage setting (default x50). For example `self.AddForex("EURUSD", Resolution.Minute, Market.FXCM)`

* Forex data

The retail forex markets are created by brokerages. QuantConnect has historical data for FXCM and OANDA Brokerages; FXCM provides 13 currency pairs since April 2007, OANDA has 71 pairs since April 2004. Because spread is important in **forex trading the data is provided in Tick and QuoteBar format. Forex data provided by the brokerages does not contain volume information**.

* To distinguish between tickers offered by different brokerages ("market places") we use a Market parameter. When you call AddForex you should specify the market you're seeking. The default market is `Market.FXCM`. If you want to use `OANDA` set `Market.Oanda`.

```py
class BootCampTask(QCAlgorithm):

    def Initialize(self):

        self.SetCash(100000)
        
        #1. Update the date range to May 1st - 31st.
        self.SetStartDate(2017, 5, 1)
        self.SetEndDate(2017, 5, 31)
        
        #1-2. Request hourly EURUSD data and set the market to Oanda
        self.eurusd = self.AddForex('EURUSD', Resolution.Hour, Market.Oanda)

    def OnData(self, data):
        pass
```

### Setting brokerage model

* Brokerage Models quickly configure the fees, fill models, slippage models and supported order types for a brokerage. This is a fastest way to setup your algorithm for your brokerage. For more information see the [documentation](https://www.quantconnect.com/docs/algorithm-reference/reality-modelling).

Reality modeling!

* Models can be used to improve the accuracy of your backtesting. We provide basic default models that assume you are trading on highly liquid assets, but if you are trading high volumes or on low volume assets, you should update these models to be more realistic.

* All models are set on a per security basis. To set a model, first fetch the security object and apply your model. Note that all models should be setup in your `Initialize` method.

```py
//Set IBM to have a constant $1 transaction fee. 
Securities["IBM"].FeeModel = new ConstantFeeTransactionModel(1); 
```

```python
class BootCampTask(QCAlgorithm):

    def Initialize(self):

        self.SetCash(100000)
        self.SetStartDate(2017, 5, 1)
        self.SetEndDate(2017, 5, 31) 
        self.forex = self.AddForex("EURUSD", Resolution.Hour, Market.Oanda)
        
        #1. Request the OANDA brokerage model
        self.SetBrokerageModel(BrokerageName.OandaBrokerage)
        
    def OnData(self, data):
        pass
```

### Accessing quote prices

* Forex data in QuantConnect is delivered as bid and ask quotes. Over time these prices are aggregated into Bid Bars and Ask Bars which show the range of prices over the period. You can access this bar data from the OnData(self, data) event handler:

```python
bid = data["EURUSD"].Bid # Bid QuoteBar
ask = data["EURUSD"].Ask # Ask QuoteBar
midpoint = data["EURUSD"].Close # Midpoint Value (i.e. where bid/ask meet?)
```

Quote bars have properties of Open, High, Low and Close. For ease of use mid-points of the Bid and Ask are also provided: bar = data["EURUSD"].Close

* Cashbook : Forex assets are virtual pairs of two currencies (e.g. EURUSD is EUR and USD). Each of these currencies is stored in your portfolio cashbook dictionary. This can be accessed with the currency symbol: e.g. `self.Portfolio.CashBook["EUR"].Amount`.

```python
class BootCampTask(QCAlgorithm):

    def Initialize(self):

        self.SetCash(100000)
        self.SetStartDate(2017, 5, 1)
        self.SetEndDate(2017, 5, 31)
        self.AddForex("EURUSD", Resolution.Hour, Market.Oanda)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage)
        self.eurusdAskClosePrice = 0

    def OnData(self, data):
        # 1. Debug the close of ask price of the "EURUSD" hourly bar at 05/01/2017 10am
        # Check the self.Time property then
        if self.Time.hour == 10 and self.Time.day == 1: 
            # Save the value and print the close of ask price
            self.eurusdAskClosePrice = data['EURUSD'].Ask.Close
            self.Debug(str(self.eurusdAskClosePrice))
```

### Applying lot size rounding

Determining Lot Sizes

Currencies in forex are traded at predetermined lot sizes. The specific lot size depends on the brokerage and currency pair. Most brokerages are rounded to the nearest 1,000 while OANDA has a lot size of 1. Crypto exchanges have a fractional lot size.

Order Rounding

* If you place an order for a lot size not supported by your brokerage it will be automatically rounded down to the nearest size. This sends a warning so where possible you should round the order before sending. You can round to the lot size with the SymbolProperty like this:

```py
# Get Lot Size
self.lotSize = self.Securities[symbol].SymbolProperties.LotSize
# Round quantity to lotsize 
rounded = round(self.orderQuantity/self.lotSize) * self.lotSize 
```

In addition to `LotSize`, the `SymbolProperties` property includes `MinimumPriceVariation`, `QuoteCurrency`, and `ContractMultiplier`.

```py
class BootCampTask(QCAlgorithm):
 
    def Initialize(self):

        self.SetCash(100000)
        self.SetStartDate(2017, 5, 1)
        self.SetEndDate(2017, 5, 31)
        self.eurusd = self.AddForex("EURUSD", Resolution.Hour, Market.Oanda)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage)
        
        #1. Save lot size to "self.lotSize"
        self.lotSize = self.Securities["EURUSD"].SymbolProperties.LotSize
        
        #2. Print the lot size:
        self.Debug("The lot size is " + str(self.lotSize ))
        
        #3. Round the order to the log size, save result to "self.roundedOrderSize"
        self.orderQuantity = 20180.12
        self.roundedOrderSize =  self.lotSize*round(self.orderQuantity / self.lotSize)
        self.Debug("The order size is " + str(self.roundedOrderSize))
        
    def OnData(self, data):
        pass
```

### Placing Forex Orders

* Market Orders

Market Orders are sent immediately and filled at the market price for the security. To send a market order, you must provide a symbol and quantity. If you do not have sufficient capital for the purchase, your order will be rejected. By default, market orders are synchronous and fill immediately.

* Limit Orders

Limit orders fill once the asset price is equal or better than the configured price. When purchasing an asset, this means the price is equal or lower to the price you set. Conversely, when selling shares, this is when the price is equal or higher to the price you set. Limit orders are often used to get a good entry price, or take-profit on an existing holding.

* Placing trades with Forex is identical to other asset types.
  
```py
self.MarketOrder("EURUSD", 12000)
self.LimitOrder("EURUSD", 12000, 1.11)
```

### Set Holdings Helper

SetHoldings is a helper method which places a market order according to the buying power weight entered. Forex trades are typically done at relatively high leverage and Forex assets in LEAN have a default leverage of 50x so it is possible to set holdings to 50x of portfolio value.

```py
self.SetHoldings("EURUSD", 50) # fill a market order worth 50x the portfolio value 
```

**All profit and loss in forex transactions is reported in USD**. Learn more about the QuantConnect Forex trading API in the documentation.

* More details on the `SetHoldings` method: The `SetHoldings` method automatically calculates the number of asset units to purchase according to the fraction of the portfolio value provided. This is a quick way to set up a portfolio with a set of weights for assets. If you already have holdings, you may want to liquidate the existing holdings first to free up buying power.

```py
 # Allocate 50% of buying power to IBM via market orders.
self.SetHoldings("IBM", 0.5)

# Allocate 50% of portfolio value to IBM, but liquidate other holdings before starting
self.SetHoldings("IBM", 0.5, True)
```

Finally the Bootcamp task completed.

```py
class BootCampTask(QCAlgorithm):

    def Initialize(self):
        self.SetCash(100000)
        self.SetStartDate(2017, 5, 1)
        self.SetEndDate(2017, 5, 31)
        
        # set the brokerage model ... 
        self.SetBrokerageModel(BrokerageName.OandaBrokerage)
        
        #1. Request the historical forex data from Oanda brokerage
        self.audusd = self.AddForex("AUDUSD", Resolution.Hour, Market.Oanda)
        
        # 3.a calculate the ordersize according to the current market lotisze
        self.lotSize = self.audusd.SymbolProperties.LotSize 
        self.ordersize = round(2000/self.lotSize) *self.lotSize
        
    def OnData(self, data):
       
        #3. Using "Portfolio.Invested" submit 1 order for 2000 AUDUSD:
        if not self.Portfolio.Invested:
            self.MarketOrder("AUDUSD", self.ordersize)
    
```

Bootcamp (Buy and hold with trailing stops)
-------------------------------------------

* Creating a Stop Order

We typically set a stop loss to trigger below the holding price of an existing holding. The difference between the holding price and the stop price is how much we are prepared to lose.

There are two kinds of stop orders in QuantConnect, stop-limit and stop-market orders. A stop-market order needs to know the quantity of shares to sell (or buy) and the price to trigger the order. The StopMarketOrder() method has the following arguments: ticker, quantity, and stopPrice.

```py
# Sell 300 units of IBM at or below 95% of the current close price
self.StopMarketOrder("IBM", -300, 0.95 * self.Securities["IBM"].Close)
```  

* An example algo with Stoporder placed.

```py
class BootCampTask(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018, 12, 1) # Set Start Date
        self.SetEndDate(2019, 4, 1) # Set End Date
        self.SetCash(100000) # Set Strategy Cash
        
        #1. Subscribe to SPY in raw mode
        self.spy = self.AddEquity("SPY", Resolution.Daily)
        self.spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
        
    def OnData(self, data):
        
        if not self.Portfolio.Invested: # if pfolio not invested
            #2. Create market order to buy 500 units of SPY
            self.MarketOrder("SPY", 500)
            #3. Create a stop market order to sell 500 units at 90% of the SPY current price
            self.StopMarketOrder("SPY", -500, 0.90*self.Securities["SPY"].Close)
```

* Understanding Order Events

Order events are updates on the status of your order. Every order event is sent to the def OnOrderEvent() event handler, with information about the order status held in an OrderEvent object.

```py
def OnOrderEvent(self, orderEvent):
    pass
```

The OrderEvent object has a Status property with the OrderStatus enum values Submitted, PartiallyFilled, Filled, Canceled, and Invalid. It also contains an OrderId property which is a unique number representing the order.

* Listening to Fills

In our algorithm, we want to listen to complete fills so we know when our stop was triggered. We can ignore the other events by explicitly looking for the Filled status.

```py
if orderEvent.Status == OrderStatus.Filled:
    # Print out the order Id
    self.Debug(orderEvent.OrderId)
```

### Tracking with Order Tickets

* When placing an order, QuantConnect returns an OrderTicket object which can be used to update an order's properties, request that it is cancelled, or fetch its OrderId.

```py
# Place our order and return an order ticket
self.stopMarketTicket = self.StopMarketOrder("IBM", -300, ibmStockPrice * 0.9)
#  Log its OrderId
self.Debug(self.stopMarketTicket.OrderId) 
```

* Identifying When a Stop Order Is Filled

The OrderId is stored on the orderEvent parameter passed into our `OnOrderEvent()` method. We can match the orderEvent.OrderId with the Id of the stop market order to see if our order has been filled.

```py
# Check if we hit our stop market
if self.stopMarketTicket is not None and orderEvent.OrderId == self.stopMarketTicket.OrderId:
    self.stopMarketFillTime = self.Time;
```

* Controlling Algorithm Re-Entry

An algorithm can place hundreds of trades in a second, so it's important to carefully control when it places trades. Ask yourself these questions when tracking your algorithm state, such as:

* When was the last time I placed a trade?
* Did the order fill according to my expectations?
* Am I placing the right number of orders?

```py
# Check that at least 15 days (~2 weeks) have passed since we last hit our limit order
if (self.Time - self.stopMarketFillTime).days < 15:
    return
```

* Bootcamp task: place stop order, check if stoporder filled, and if so reenter 15 days after the stoporder has been filled.

```py
class BootCampTask(QCAlgorithm):
    
    # Order ticket for our stop order, Datetime when stop order was last hit
    stopMarketTicket = None
    stopMarketFillTime = datetime.min
    
    def Initialize(self):
        self.SetStartDate(2018, 12, 1)
        self.SetEndDate(2019, 4, 1)
        self.SetCash(100000)
        spy = self.AddEquity("SPY", Resolution.Daily)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
    def OnData(self, data):
        
        #4. Check that at least 15 days (~2 weeks) have passed since we last hit our stop order
    
        reenter = self.stopMarketFillTime is None or (self.Time - self.stopMarketFillTime).days >= 15
        
        if not reenter: 
            return 
        else: 
            # we are ready to invest 
            if not self.Portfolio.Invested:
                self.MarketOrder("SPY", 500)
                #1. Create stop loss through a stop market order at 90% of the current close price
                stopPrice = 
                self.stopMarketTicket = self.StopMarketOrder("SPY", -500, .9*self.Securities["SPY"].Close)
      
    def OnOrderEvent(self, orderEvent):
        
        if orderEvent.Status != OrderStatus.Filled:
            return
        
        # Printing the security fill prices.
        self.Debug(self.Securities["SPY"].Close)
        
        #2. Check if we hit our stop loss (Compare the orderEvent.Id with the stopMarketTicket.OrderId)
        if self.stopMarketTicket and self.stopMarketTicket.OrderId == orderEvent.OrderId : 
            self.stopMarketFillTime = self.Time
            #3. Store datetime
            self.Debug(self.Time)
```

### Creating a trailing stop-loss

* Buy and Hold with a Trailing Stop Creating a Trailing Stop Loss

By updating a stop's trigger price as the market moves, we can in theory lock in profits and cap downside risk. This transforms our static risk management into a dynamic one.

* Updating Orders

Orders which are not filled immediately can be updated using their order ticket. To update an order you create an UpdateOrderFields object which contains all the properties you'd like to change.

To update the stop price of a given order ticket, we invoke `orderticket.Update()`. This updates the stopprice as the current close price of the security.

```py
# Update stop loss price using UpdateOrderFields helper.
updateFields = UpdateOrderFields()
updateFields.StopPrice = self.Securities["SPY"].Close * 0.9
self.stopMarketTicket.Update(updateFields)
```

Implementing a trailing stop-loss in a Quantconnect algorithm

```py
class BootCampTask(QCAlgorithm):
    
    # Order ticket for our stop order, Datetime when stop order was last hit
    stopMarketTicket = None
    stopMarketOrderFillTime = datetime.min
    highestSPYPrice = 0
    
    def Initialize(self):
        self.SetStartDate(2018, 12, 1)
        self.SetEndDate(2018, 12, 10)
        self.SetCash(100000)
        spy = self.AddEquity("SPY", Resolution.Daily)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
    def OnData(self, data):
        
        if (self.Time - self.stopMarketOrderFillTime).days < 15:
            return

        if not self.Portfolio.Invested:
            self.MarketOrder("SPY", 500)
            self.stopMarketTicket = self.StopMarketOrder("SPY", -500, 0.9 * self.Securities["SPY"].Close)
        
        else:
            #1. Check if the SPY price is higher that highestSPYPrice.
            if self.Securities["SPY"].Close > self.highestSPYPrice : 
                #2. Save the new high to highestSPYPrice; then update the stop price to 90% of highestSPYPrice 
                self.highestSPYPrice = self.Securities["SPY"].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.highestSPYPrice * 0.9
                self.stopMarketTicket.Update(updateFields)
                #3. Print the new stop price with Debug()
                self.Debug("new stop prices is {}".format(self.highestSPYPrice))
                
    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.Filled:
            return
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketOrderFillTime = self.Time
```

### Visualizing the Stop Levels

* Buy and Hold with a Trailing Stop Visualizing the Stop Levels

Charts are a powerful way of visualizing the behavior of your algorithm. See the ]documentation](<https://www.quantconnect.com/docs/algorithm-reference/charting>) for more details on the charting API.

* Creating a Chart

The Plot() method can draw a line-chart with a single line of code. It takes three arguments, the name of the chart, the name of the series and the value you'd like to plot.

```py
# You can plot multiple series on the same chart.
self.Plot("Levels", "Asset Price", self.Securities["IBM"].Price)
self.Plot("Levels", "Stop Price",  self.Securities["IBM"].Price * 0.9)
```

The Plot() function is highly versatile and takes care of plotting to the correct chart and series.

Plotting shall be done during some events, e.g. OnData event etc. in the QCAlgorithm.

```py
class BootCampTask(QCAlgorithm):
    
    # Order ticket for our stop order, Datetime when stop order was last hit
    stopMarketTicket = None
    stopMarketOrderFillTime = datetime.min
    highestSPYPrice = -1
    
    def Initialize(self):
        self.SetStartDate(2018, 12, 1)
        self.SetEndDate(2018, 12, 10)
        self.SetCash(100000)
        spy = self.AddEquity("SPY", Resolution.Daily)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
    def OnData(self, data):
        
        # 1. Plot the current SPY price to "Data Chart" on series "Asset Price"
        self.Plot("Data Chart", "Asset Price" ,  self.Securities["SPY"].Close)
        if (self.Time - self.stopMarketOrderFillTime).days < 15:
            return

        if not self.Portfolio.Invested:
            self.MarketOrder("SPY", 500)
            self.stopMarketTicket = self.StopMarketOrder("SPY", -500, 0.9 * self.Securities["SPY"].Close)
        
        else:
            
            #2. Plot the moving stop price on "Data Chart" with "Stop Price" series name
            self.Plot("Data Chart", "Stop Price", self.highestSPYPrice)
            if self.Securities["SPY"].Close > self.highestSPYPrice:
                
                self.highestSPYPrice = self.Securities["SPY"].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.highestSPYPrice * 0.9
                self.stopMarketTicket.Update(updateFields) 
            
    def OnOrderEvent(self, orderEvent):
        
        if orderEvent.Status != OrderStatus.Filled:
            return
        
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketOrderFillTime = self.Time
```

Bootcamp (Momentum-Based Tactical Allocation)
---------------------------------------------

TODO
