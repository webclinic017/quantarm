#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
"""计算28轮动某个标的池的盈利情况"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeed


# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('period', 20),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.order = None
        self.month = -1
        self.mom = [bt.indicators.MomentumOscillator(
            i, period=self.params.period) for i in self.datas]

    def next(self):
        # Simply log the closing price of the series from the reference
        buy_id = 0

        c = [i.momosc[0] for i in self.mom]
        c[0] = 0
        index, value = c.index(max(c)), max(c)
        if value > 100:
            buy_id = index

        # print("buy_id ", buy_id)

        for i in range(0, len(c)):
            if i != buy_id:
                position_size = self.broker.getposition(
                    data=self.datas[i]).size
                if position_size != 0:
                    self.order_target_percent(data=self.datas[i], target=0)
        position_size = self.broker.getposition(data=self.datas[buy_id]).size
        if position_size == 0:
            self.order_target_percent(data=self.datas[buy_id], target=0.98)

    def stop(self):
        # print(self.broker.getvalue())
        return_all = self.broker.getvalue() / 1200000.0
        print('{0},{1}%,{2}%'.format(self.params.period,
                                     round((return_all - 1.0) * 100, 2),
                                     round(
                                         (pow(return_all, 1.0 / 8) - 1.0) * 100, 2)
                                     ))


class TSCSVData(btfeed.GenericCSVData):
    params = (
        ("fromdate", datetime.datetime(2012, 1, 1)),
        ("todate", datetime.datetime(2019, 12, 31)),
        ('nullvalue', 0.0),
        ('dtformat', ('%Y-%m-%d')),
        ('openinterest', -1)
    )


def backtest(cash, files, periods):
    files = files
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.optstrategy(TestStrategy, period=periods)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    for i in files:
        datapath = os.path.join(modpath, '{0}'.format(i))

        # Create a Data Feed
        data = TSCSVData(dataname=datapath)

        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(0.0005)

    # Run over everything
    print("period,Total ROI,Annual ROI")
    cerebro.run()


if __name__ == '__main__':
    """第0个标的是默认标的"""
    files = ['widthfund_5m/510050.XSHG.csv', 'widthfund_5m/159949.XSHE.csv']
    cash = 1200000.0
    periods = range(0, 60)
    backtest(cash, files, periods)
