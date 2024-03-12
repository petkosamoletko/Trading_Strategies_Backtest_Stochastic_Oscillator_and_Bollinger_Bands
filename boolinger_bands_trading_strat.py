import datetime
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from pandas_datareader import data as pdr
import backtrader as bt
import yfinance as yf
yf.pdr_override()

# inspiration for strategy 
# https://www.youtube.com/watch?v=CxFv_EUY0ZA&t

def get_stock_data(stock, timeframe_years):
    endDate = datetime.datetime.now()
    delta = datetime.timedelta(365 * timeframe_years)
    startDate = endDate - delta
    stockData = pdr.get_data_yahoo(stock, startDate, endDate)
    
    startDate = stockData.index[0]
    endDate = stockData.index[-1]
    
    
    print("Start Date:", startDate.strftime("%B %d, %Y, %I:%M:%S %p"))
    print("End Date:", endDate.strftime("%B %d, %Y, %I:%M:%S %p"))
    
    return stockData, startDate, endDate 

df, startDate, endDate = get_stock_data("EOG", 15)
feed = bt.feeds.PandasData(dataname = df)

class FixedCommision(bt.CommInfoBase):
    '''
    may need some tweaking
    '''
    paras = (
    ("commision", 10),
    ("stocklike", True),
    ("commtype", bt.CommInfoBase.COMM_FIXED)
    )
    
    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission
    
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders
        self.order = None
        self.qty_sell_track = 0 
        self.log_buy = 0 
        self.log_sell = 0 
        self.times_traded = 0
        
        self.moving_avg = bt.ind.SMA(period = 200)
        self.boll_bands = bt.ind.BollingerBands(period = 20, devfactor = 2.5)
        self.rsi = bt.indicators.RSI(period = 2, safediv = True)

        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
                self.log('TOTAL BUY EXECUTED, %.2f' % (order.executed.price * self.position.size))
                self.log_buy = order.executed.price * self.position.size
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
                self.log('SELL EXECUTED, %.2f' % (order.executed.price * self.qty_sell_track))
                print("")
                self.log_sell = order.executed.price * self.qty_sell_track
                if (self.log_sell - self.log_buy) > 0:
                    print("Positive aka win buy/sell", round((self.log_sell - self.log_buy),2))
                else:
                    print("Negative aka loss buy/sell", round((abs(self.log_sell - self.log_buy)), 2))
                
                self.log_sell = 0
                
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.datas[0].close[0] > self.moving_avg and self.datas[0].close[0] < self.boll_bands.lines.bot:
                    # price
                    print("*" * 10)
                    print("date occurance", self.datas[0].datetime.date(0))
                    print("close p", self.datas[0].close[0])
                    # top tva ti bachka -> pravilnite dati izbira
                    target_p = self.datas[0].close[0] * 0.97
                    print("target p", target_p)
                    # buy condition
                    
                    
                    # qty
                    available_funds = self.broker.get_cash()
                    qty = math.floor(available_funds/target_p)
                    if qty > 0:
                        print("buy qty", qty)
                        # initiliaze back to 0
                        self.qty_sell_track = 0 
                        self.order = self.buy(exectype=bt.Order.Limit,
                                             price = target_p,
                                             size = qty)
                        self.log_buy = 0
                

        else:

            # Already in the market ... we might sell
            # sell condition 10 days or when the self.rsi is above 50 
            if len(self) >= (self.bar_executed + 10) or self.rsi > 50:
                if len(self) >= (self.bar_executed + 10):
                    print("Execution due to day conditions")
                if self.rsi > 50:
                    print("Execution due to RSI")

                print("")
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                qty_to_sell = self.position.size

                if qty_to_sell > 0:
                    self.qty_sell_track = qty_to_sell
                    print("sell qty", qty_to_sell)
                    self.order = self.sell(size=qty_to_sell)
                    print("")
                    self.times_traded += 1
                    
    def stop(self):
        print("")
        print("*" * 10)
        print("End Summary for Bollinger Band Trading System")
        print("Times in market:", self.times_traded)        


cerebro = bt.Cerebro()
cerebro.addstrategy(TestStrategy)
cerebro.adddata(feed)
cerebro.broker.setcash(12000.0)

comminfo = FixedCommision()
cerebro.broker.addcommissioninfo(comminfo)

# Print out the starting conditions

start = cerebro.broker.getvalue()
cerebro.run()
end = cerebro.broker.getvalue()
print('Starting Portfolio Value: %.2f' % start)
print('Final Portfolio Value: %.2f' % end)
print('Gross Return: %.2f' %(end-start))

cerebro.plot(style = "candlestick")
