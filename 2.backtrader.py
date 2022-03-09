from turtle import shapesize
from matplotlib.style import available
import pandas as pd
from pylab import mpl
import matplotlib.pyplot as plt
from datetime import datetime
import backtrader as bt
import tushare as ts
# backtrader_plotting 的版本需要调整到 1.1.0y
from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo

mpl.rcParams['axes.unicode_minus'] = False

# 正常显示画图时出现的中文和负号
mpl.rcParams['font.sans-serif'] = ['SimHei']


class my_strategy1(bt.Strategy):
    params = (
        ('period', 15),
        ('printlog', False)
    )

    def __init__(self):
        self.dataclose = self.data0.close
        self.ma = bt.indicators.MovingAverageSimple(
            self.data0, period=self.params.period)
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def next(self):
        # print('获取当前总资产', cerebro.broker.getvalue())
        # print(self.position)
        cur_price = self.data0.close[0]
        aval_cash = self.broker.getcash()
        size = int(aval_cash / (100*cur_price))*100
        cur_date = bt.num2date(self.datas[0].lines[6][0])
        # print('获取当前总资产', cerebro.broker.getcash())
        # print('当前价格', self.data0.close[0])
        # print(siz)
        # print(self.order)
        if(self.order):
            return
        if (not self.position):
            # print(self.broker.getposition(self.data).size, '-0----0-')
            # print(self.ma[0], '15日均线')
            # print(self.dataclose[0], cur_date, '收盘价')
            if self.dataclose[0] > self.ma[0]:
                # print(cur_date, '当前是买，收盘价', cur_price)
                self.order = self.buy(size=size)

        else:
            if self.dataclose[0] < self.ma[0]:
                # print(self.position.size)
                # print(cur_date, '当前是卖，价格是', cur_price)
                # self.order = self.sell(size=size)
                self.order = self.close()
    # 交易记录日志（可省略，默认不输出结果）

    def log(self, txt, dt=None, doprint=False):
        #         注意：在作弊模式下，notify_order中输出self.data0.datetime.datetime(0)并不是订单执行时间，而是次日。
        # 正确的 获取订单执行时间order.executed.dt、获取订单创建时间order.created.dt
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()},{txt}')

    # 记录交易执行情况（可省略，默认不输出结果）
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入:\n价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'卖出:\n价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}')
            self.bar_executed = len(self)

        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('交易失败')
        self.order = None

    # 记录交易收益情况（可省略，默认不输出结果）
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}')

    def stop(self):

        portvalue = self.broker.getvalue()
        pnl = portvalue - 200000
        # 打印结果
        print(f'净收益: {round(pnl,2)}')
        print(f'总资金: {round(portvalue,2)}')
        print(f'总收益率: {(round(pnl,2) * 100)/round(200000,2)}%')
        self.log('(MA均线： %2d日) 期末总资金 %.2f' %
                 (self.params.period, self.broker.getvalue()), doprint=True)


def get_data(code, start='2018-01-01', end='2022-02-31'):
    df = ts.get_k_data(code, autype='qfq', start=start, end=end)
    df.index = pd.to_datetime(df.date)
    df['openinterest'] = 0
    df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    return df


def main():
    dataframe = get_data('600519')

    # 回测期间
    start = datetime(2019, 3, 31)
    end = datetime(2021, 3, 31)
    # 加载数据
    data = bt.feeds.PandasData(dataname=dataframe, fromdate=start, todate=end)

    # 初始化cerebro回测系统设置
    cerebro = bt.Cerebro()
    # 将数据传入回测系统
    cerebro.adddata(data)
    # 将交易策略加载到回测系统中
    cerebro.optstrategy(my_strategy1, period=range(3, 6), printlog=False)

    # cerebro.addstrategy(my_strategy1, printlog=True)
    # 设置初始资本为10,000
    startcash = 200000
    cerebro.broker.setcash(startcash)
    # 设置交易手续费为 万分之2
    cerebro.broker.setcommission(commission=0)
    cerebro.broker.set_coc(True)

    d1 = start.strftime('%Y%m%d')
    d2 = end.strftime('%Y%m%d')
    print(f'初始资金: {startcash}\n回测期间：{d1}:{d2}')
    # 运行回测系统
    cerebro.run()

    # b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    # cerebro.plot(b)

    # cerebro.plot(style='candlestick')

    # 获取回测结束后的总资金
    # portvalue = cerebro.broker.getvalue()
    # pnl = portvalue - startcash
    # # 打印结果
    # print(f'净收益: {round(pnl,2)}')
    # print(f'总资金: {round(portvalue,2)}')
    # print(f'总收益率: {(round(pnl,2) * 100)/round(startcash,2)}%')


if __name__ == "__main__":
    main()
