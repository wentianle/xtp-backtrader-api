from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime, timedelta

from backtrader.feed import DataBase
from backtrader import date2num, num2date
from backtrader.utils.py3 import queue, with_metaclass
import backtrader as bt

from xtp_backtrader_api import xtpstore


class MetaXTPData(DataBase.__class__):
    def __init__(cls, name, bases, dct):
        """
        Class has already been created ... register
        """
        # Initialize the class
        super(MetaXTPData, cls).__init__(name, bases, dct)

        # Register with the store
        xtpstore.XTPStore.DataCls = cls


class XTPData(with_metaclass(MetaXTPData, DataBase)):
    """
    XTP Data Feed.
    """
    params = (
        ('server_ip', '127.0.0.1'),
        ('server_port', 7496),
        ('client_id', None),  # None generates a random clientid 1 -> 2^16
        ('protocol', False),
        ('debug', False),
        ('userid', 3),  # -1 forever, 0 No, > 0 number of retries
        ('password', 3.0),  # timeout between reconnections
        ('timeoffset', True),  # Use offset to server for timestamps if needed
        ('timerefresh', 60.0),  # How often to refresh the timeoffset
    )

    _store = xtpstore.XTPStore

    # States for the Finite State Machine in _load
    _ST_FROM, _ST_START, _ST_LIVE, _ST_HISTORBACK, _ST_OVER = range(5)

    _TOFFSET = timedelta()

    def _timeoffset(self):
        # Effective way to overcome the non-notification?
        return self._TOFFSET

    def islive(self):
        """
        Returns ``True`` to notify ``Cerebro`` that preloading and runonce
        should be deactivated
        """
        return True

    def __init__(self, **kwargs):
        self.o = self._store(**kwargs)

    def setenvironment(self, env):
        """
        Receives an environment (cerebro) and passes it over to the store it
        belongs to
        """
        super(XTPData, self).setenvironment(env)
        env.addstore(self.o)

    def start(self):
        """
        Starts the XTP connection and gets the real contract and
        contractdetails if it exists
        """
        super(XTPData, self).start()
        self.resample(timeframe=self.p.timeframe,
                      compression=self.p.compression)

    def stop(self):
        """
        Stops and tells the store to stop
        """
        super(XTPData, self).stop()

    def _load(self):
        try:
            data = self.o.notifs.popleft()
        except IndexError:
            return None  # no data in the queue

            # fill the lines
            self.lines.datetime[0] = date2num(
                time.strptime(time.data.data_time, "%Y%m%d%H%M%S%f"))

            self.lines.open[0] = data.open_price
            self.lines.high[0] = data.high_price
            self.lines.low[0] = data.low_price
            self.lines.close[0] = data.close_price
            self.lines.volume[0] = data.qty
            self.lines.openinterest[0] = data.total_long_positon
            return True
