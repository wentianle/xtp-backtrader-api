from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections

from backtrader import BrokerBase, Order, BuyOrder, SellOrder
from backtrader.utils.py3 import with_metaclass, iteritems
from backtrader.comminfo import CommInfoBase
from backtrader.position import Position

from xtp_backtrader_api import xtpstore


class XTPCommInfo(CommInfoBase):
    def getvaluesize(self, size, price):
        # In real life the margin approaches the price
        return abs(size) * price

    def getoperationcost(self, size, price):
        """
        Returns the needed amount of cash an operation would cost
        """
        # Same reasoning as above
        return abs(size) * price


class MetaXTPBroker(BrokerBase.__class__):
    def __init__(cls, name, bases, dct):
        """
        Class has already been created ... register
        """
        # Initialize the class
        super(MetaXTPBroker, cls).__init__(name, bases, dct)
        xtpstore.XTPStore.BrokerCls = cls


class XTPBroker(with_metaclass(MetaXTPBroker, BrokerBase)):
    """
    Broker implementation for XTP.

    This class maps the orders/positions from XTP to the
    internal API of ``backtrader``.

    Params:

      - ``use_positions`` (default:``True``): When connecting to the broker
        provider use the existing positions to kickstart the broker.

        Set to ``False`` during instantiation to disregard any existing
        position
    """
    params = (
        ('use_positions', True),
    )

    def __init__(self, **kwargs):
        super(XTPBroker, self).__init__()

        self.o = xtpstore.XTPStore(**kwargs)

        self.orders = collections.OrderedDict()  # orders by order id
        self.notifs = collections.deque()  # holds orders which are notified

        self.opending = collections.defaultdict(list)  # pending transmission
        self.brackets = dict()  # confirmed brackets

        self.startingcash = self.cash = 0.0
        self.startingvalue = self.value = 0.0
        self.addcommissioninfo(self, XTPCommInfo(mult=1.0, stocklike=False))

    def update_positions(self):
        """
        this method syncs the XTP real broker positions and the Backtrader
        broker instance. the positions is defined in BrokerBase(in getposition)
        and used in bbroker (the backtrader broker instance) with Data as the
        key. so we do the same here. we create a defaultdict of Position() with
        data as the key.
        :return: collections.defaultdict ({data: Position})
        """
        positions = collections.defaultdict(Position)
        if self.p.use_positions:
            broker_positions = self.o.oapi.list_positions()
            broker_positions_symbols = [p.symbol for p in broker_positions]
            broker_positions_mapped_by_symbol = \
                {p.symbol: p for p in broker_positions}

            for name, data in iteritems(self.cerebro.datasbyname):
                if name in broker_positions_symbols:
                    size = int(broker_positions_mapped_by_symbol[name].qty)
                    positions[data] = Position(
                        size,
                        float(broker_positions_mapped_by_symbol[
                            name].avg_entry_price)
                    )
        return positions

    def start(self):
        super(XTPBroker, self).start()
        self.addcommissioninfo(self, XTPCommInfo(mult=1.0, stocklike=False))
        self.o.start(broker=self)
        self.startingcash = self.cash = self.o.get_cash()
        self.startingvalue = self.value = self.o.get_value()
        self.positions = self.update_positions()

    def data_started(self, data):
        pos = self.getposition(data)

        if pos.size < 0:
            order = SellOrder(data=data,
                              size=pos.size, price=pos.price,
                              exectype=Order.Market,
                              simulated=True)

            order.addcomminfo(self.getcommissioninfo(data))
            order.execute(0, pos.size, pos.price,
                          0, 0.0, 0.0,
                          pos.size, 0.0, 0.0,
                          0.0, 0.0,
                          pos.size, pos.price)

            order.completed()
            self.notify(order)

        elif pos.size > 0:
            order = BuyOrder(data=data,
                             size=pos.size, price=pos.price,
                             exectype=Order.Market,
                             simulated=True)

            order.addcomminfo(self.getcommissioninfo(data))
            order.execute(0, pos.size, pos.price,
                          0, 0.0, 0.0,
                          pos.size, 0.0, 0.0,
                          0.0, 0.0,
                          pos.size, pos.price)

            order.completed()
            self.notify(order)

    def stop(self):
        super(XTPBroker, self).stop()
        self.o.stop()

    def getcash(self):
        # This call cannot block if no answer is available from XTP
        self.cash = cash = self.o.get_cash()
        return cash

    def getvalue(self, datas=None):
        """
        if datas then we will calculate the value of the positions if not
        then the value of the entire portfolio (positions + cash)
        :param datas: list of data objects
        :return: float
        """
        if not datas:
            # don't use self.o.get_value(). it takes time for local store to
            # get update from broker.
            self.value = float(self.o.oapi.get_account().portfolio_value)
            return self.value
        else:
            # let's calculate the value of the positions
            total_value = 0
            for d in datas:
                pos = self.getposition(d)
                if pos.size:
                    price = list(d)[0]
                    total_value += price * pos.size
            return total_value

    def getposition(self, data, clone=True):
        pos = self.positions[data]
        if clone:
            pos = pos.clone()

        return pos

    def orderstatus(self, order):
        o = self.orders[order.ref]
        return o.status

    def buy(self, owner, data,
            size, price=None, plimit=None,
            exectype=None, valid=None, tradeid=0, oco=None,
            trailamount=None, trailpercent=None,
            parent=None, transmit=True,
            **kwargs):

        order = BuyOrder(owner=owner, data=data,
                         size=size, price=price, pricelimit=plimit,
                         exectype=exectype, valid=valid, tradeid=tradeid,
                         trailamount=trailamount, trailpercent=trailpercent,
                         parent=parent, transmit=transmit)

        order.addinfo(**kwargs)
        order.addcomminfo(self.getcommissioninfo(data))
        return self._transmit(order)

    def sell(self, owner, data,
             size, price=None, plimit=None,
             exectype=None, valid=None, tradeid=0, oco=None,
             trailamount=None, trailpercent=None,
             parent=None, transmit=True,
             **kwargs):

        order = SellOrder(owner=owner, data=data,
                          size=size, price=price, pricelimit=plimit,
                          exectype=exectype, valid=valid, tradeid=tradeid,
                          trailamount=trailamount, trailpercent=trailpercent,
                          parent=parent, transmit=transmit)

        order.addinfo(**kwargs)
        order.addcomminfo(self.getcommissioninfo(data))
        return self._transmit(order)

    def cancel(self, order):
        if not self.orders.get(order.ref, False):
            return
        if order.status == Order.Cancelled:  # already cancelled
            return

        return self.o.order_cancel(order)

    def notify(self, order):
        self.positions = self.update_positions()
        self.notifs.append(order.clone())

    def get_notification(self):
        if not self.notifs:
            return None

        return self.notifs.popleft()

    def next(self):
        self.notifs.append(None)  # mark notification boundary
