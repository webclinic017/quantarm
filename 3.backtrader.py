import backtrader as bt
from datetime import datetime
from turtle import position
import pandas as pd
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt

# 正常显示画图时出现的中文和负号
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


class Mystrtegy(bt.Strategy):
    params = (('maperiod', 15),
              ('printlog', False),)

    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close
        self.ma = bt.indicators.MovingAverageSimple(
            self.datas[0], period=self.params.maperiod)

    def next(self):
        # print(self.data0.lines.datetime.date(0), self.ma[0])
        cur_date = self.data0.lines.datetime.date(0)
        daad_date = datetime.strptime('2019-01-01', '%Y-%m-%d').date()
        # print(type(daad_date))
        if cur_date < daad_date:
            return
        if(self.order):
            return
        print(self.params.maperiod, cur_date)
        if(not self.position):
            if(self.dataclose[0] > self.ma[0]):
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.ma[0]:
                self.order = self.sell()

        # 交易记录日志（可省略，默认不输出结果）

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    def stop(self):
        self.log('(MA均线： %2d日) 期末总资金 %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)


def main(code, start, end='', startcash=10000, qts=500, com=0.001):
    # 创建主控制器
    cerebro = bt.Cerebro()
    # 导入策略参数寻优
    cerebro.optstrategy(Mystrtegy, maperiod=range(3, 31))
    # 获取数据
    df = ts.get_k_data(code, autype='qfq', start=start)
    df.index = pd.to_datetime(df.date)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    print(df)
    # 将数据加载至回测系统
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    # broker设置资金、手续费
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=com)
    # 设置买入设置，策略，数量
    cerebro.addsizer(bt.sizers.FixedSize, stake=qts)
    print('期初总资金: %.2f' %
          cerebro.broker.getvalue())
    cerebro.run(maxcpus=1)
    print('期末总资金: %.2f' % cerebro.broker.getvalue())


main('600519', '2018-01-01', '', 1000000, 100)
