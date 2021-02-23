# This is the example code from the repo's README
import xtp_backtrader_api
import backtrader as bt
from datetime import datetime


class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)

    store = xtp_backtrader_api.XTPStore(userid='53191002899', password='778MhWYa',
                                        client_id=1, server_ip='120.27.164.138', server_port=6002, debug=True)

    DataFactory = store.getdata  # or use xtp_backtrader_api.AlpacaData

    data0 = DataFactory(dataname=symbol, historical=True,
                        fromdate=datetime(
                            2015, 1, 1), timeframe=bt.TimeFrame.Days)
    broker = store.getbroker()
    cerebro.setbroker(broker)
    cerebro.adddata(data0)

    print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.run()
    print('Final Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.plot()
