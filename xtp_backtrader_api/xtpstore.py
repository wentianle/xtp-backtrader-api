from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import collections
import time
from enum import Enum
import traceback

from datetime import datetime, timedelta, time as dtime
from dateutil.parser import parse as date_parse
import time as _time
import trading_calendars
import threading
import asyncio

import pytz
import requests
import pandas as pd

import backtrader as bt
from backtrader.metabase import MetaParams
from backtrader.utils.py3 import queue, with_metaclass

import xtpwrapper

import xtpwrapper.xtp_enum as XTPEnum
import xtpwrapper.xtp_struct as XTPStruct

NY = 'America/New_York'


# Extend the exceptions to support extra cases
class XTPError(Exception):
    """ Generic error class, catches XTP response errors
    """

    def __init__(self, error_response):
        self.error_response = error_response
        msg = "XTP API returned error code %s (%s) " % \
              (error_response['code'], error_response['message'])

        super(XTPError, self).__init__(msg)


class MetaSingleton(MetaParams):
    '''Metaclass to make a metaclassed class a singleton'''
    def __init__(cls, name, bases, dct):
        super(MetaSingleton, cls).__init__(name, bases, dct)
        cls._singleton = None

    def __call__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = (
                super(MetaSingleton, cls).__call__(*args, **kwargs))

        return cls._singleton


class XTPQuoteAPI(with_metaclass(MetaSingleton, xtpwrapper.QuoteAPI)):

    _connectStatus: bool = False
    _loginStatus: bool = False

    params = (
        ('server_ip', '127.0.0.1'),
        ('server_port', 7496),
        ('client_id', None),  # None generates a random clientid 1 -> 2^16
        ('debug', False),
        ('userid', 3),  # -1 forever, 0 No, > 0 number of retries
        ('password', 3.0),  # timeout between reconnections
        ('timeoffset', True),  # Use offset to server for timestamps if needed
        ('timerefresh', 60.0),  # How often to refresh the timeoffset
        ('ticks', []),  # How often to refresh the timeoffset
        ('notifs', collections.deque()),  # How often to refresh the timeoffset
    )

    def __init__(self):
        """"""
        super(XTPQuoteAPI, self).__init__()
        self.log_level = XTPEnum.XTP_LOG_LEVEL.XTP_LOG_LEVEL_INFO
        self.notifs = self.p.notifs
        self.CreateQuote(self.p.client_id, 'quota', self.log_level)
        self.SetHeartBeatInterval(10)
        connected = self.LoginServer()

        if connected == True:
            self.SubscribeMarketData(
                self.p.ticks, XTPEnum.XTP_EXCHANGE_TYPE.XTP_EXCHANGE_SH)

    def OnDisconnected(self, reason):
        """"""
        self._connectStatus = False
        self._loginStatus = False
        self.LoginServer()

    def OnError(self, error_info):
        print(error_info)

    def OnDepthMarketData(self, market_data, bid1_qty, bid1_count, max_bid1_count, ask1_qty, ask1_count, max_ask1_count):
        self.notifs.append(market_data)
        return

    def LoginServer(self):
        n = self.Login(
            self.p.server_ip,
            self.p.server_port,
            self.p.userid,
            self.p.password,
            XTPEnum.XTP_PROTOCOL_TYPE.XTP_PROTOCOL_TCP
        )

        if not n:
            self._connectStatus = True
            self._loginStatus = True
            msg = "行情服务器登录成功"
        else:
            msg = f"行情服务器登录失败，原因：{n}.".format(n)

        print(msg)
        return n == 0

    def Close(self):
        if self._connectStatus:
            self.exit()

    def Release(self):
        """
        删除接口对象本身
        不再使用本接口对象时,调用该函数删除接口对象
        :return: None
        """
        super().Release()


class XTPStore(with_metaclass(MetaSingleton, object)):
    '''
        Singleton class wrapping to control the connections to XTP.
    '''

    BrokerCls = None  # broker class will autoregister
    DataCls = None  # data class will auto register

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

    @classmethod
    def getdata(cls, *args, **kwargs):
        '''Returns ``DataCls`` with args, kwargs'''
        return cls.DataCls(*args, **kwargs)

    @classmethod
    def getbroker(cls, *args, **kwargs):
        '''Returns broker with *args, **kwargs from registered ``BrokerCls``'''
        return cls.BrokerCls(*args, **kwargs)

    def __init__(self):
        super(XTPStore, self).__init__()

        self.notifs = collections.deque()  # store notifications for cerebro

        self._env = None  # reference to cerebro for general notifications
        self.broker = None  # broker instance
        self.datas = list()  # datas that have registered over start
        self.quotaAPI = XTPQuoteAPI(notifs=self.notifs, userid=self.p.userid, password=self.p.password,
                                    server_ip=self.p.server_ip, server_port=self.p.server_port, ticks=['688158'], debug=self.p.debug, client_id=self.p.client_id)

    def start(self, data=None, broker=None):
        pass

    def stop(self):
        pass

    def put_notification(self, msg, *args, **kwargs):
        self.notifs.append((msg, args, kwargs))

    def get_notifications(self):
        '''Return the pending "store" notifications'''
        self.notifs.append(None)  # put a mark / threads could still append


if __name__ == '__main__':

    session_id = 0
    request_id = 1
    test = XTPStore(userid='53191002899', password='778MhWYa',
                    client_id=1, server_ip='120.27.164.138', server_port=6002, debug=True)

    while(True):
        if len(test.notifs):
            print("===========", test.notifs.pop())
        time.sleep(1)
