#imports
import datetime
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from pandas_datareader import data as pdr
import backtrader as bt
import yfinance as yf
from datetime import timedelta
yf.pdr_override()

# inspiration for strategy 
# https://www.youtube.com/watch?v=viLst9ZAC6Y&t

def get_stock_data(stock, timeframe_years):
    endDate = datetime.datetime.now()
    delta = datetime.timedelta(365 * timeframe_years)
    startDate = endDate - delta
    stockData = pdr.get_data_yahoo(stock, startDate, endDate)
    
    startDate = stockData.index[0]
    endDate = stockData.index[-1]
    
    return stockData, startDate, endDate 


df, startDate, endDate = get_stock_data("EOG", 15)
feed = bt.feeds.PandasData(dataname = df)
print("Start Date:", startDate.strftime("%B %d, %Y, %I:%M:%S %p"))
print("End Date:", endDate.strftime("%B %d, %Y, %I:%M:%S %p"))


class FixedCommision(bt.CommInfoBase):
    '''
    may need some tweaking
    if having per trade comission
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
        self.dataclose = self.datas[0].close

        # keep track of pending orders
        self.order = None
        #self.pending_buy_order = None
        
        self.moving_avg = bt.ind.SMA(period = 200)
        stochastic = bt.ind.Stochastic(self.datas[0], period = 10, period_dfast = 1, period_dslow = 1) # nothing for the d as we dont take it into consideration
        #self.stochastic_k = stochastic.lines.percK
        self.stochastic_k = stochastic.percK
        self.times_traded = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Note that a broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        if self.order:
            return

        # Are we in the market?
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.datas[0].close[0] > self.moving_avg and self.stochastic_k <= 5:
                self.target_p = self.datas[0].close[0] * 0.97
                valid_duration = datetime.timedelta(days=5)

                
                # get current cash 
                funds = self.broker.get_cash()
                target_q = math.floor(funds/self.target_p)
                if target_q > 0:
                    print("")
                    self.log('BUY CREATE, %.2f' % self.target_p)
                    print("BUY", target_q)
                    self.pending_buy_order = self.buy(exectype=bt.Order.Limit,
                                                 price = self.target_p,
                                                 valid = valid_duration,
                                                 size = target_q)
                    #self.pending_buy_order = self.order 

        else:
            if len(self) >= (self.bar_executed + 10) or self.datas[0].close[0] > self.target_p:
                if len(self) >= (self.bar_executed + 10):
                    print("Execution due to day conditions")
                if self.datas[0].close[0] > self.target_p:
                    print("Execution due closing higher")
                # Sell if conditions are being met
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                
                qty_to_sell = self.position.size
                if qty_to_sell > 0:
                    self.order = self.sell(size = qty_to_sell)
                    print("SELL VOL:", qty_to_sell)
                    self.times_traded += 1 

    def stop(self):
        print("")
        print("*" * 10)
        print("End Summary for Stochastic Trading System")
        print("Times in market:", self.times_traded)

cerebro = bt.Cerebro()


cerebro.addstrategy(TestStrategy)
cerebro.adddata(feed)

# desired cash start
cerebro.broker.setcash(12000.0)

comminfo = FixedCommision()
cerebro.broker.addcommissioninfo(comminfo)
start = cerebro.broker.getvalue()
cerebro.run()
end = cerebro.broker.getvalue()

# Print out the final result
print('Starting Portfolio Value: %.2f' % start)
print('Final Portfolio Value: %.2f' % end)
print('Gross Return: %.2f' %(end-start))

cerebro.plot()