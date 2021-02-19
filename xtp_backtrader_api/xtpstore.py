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

import xtpwrapper.QuotaAPI as XTPQuotaAPI
import xtpwrapper.TraderAPI as XTPTraderAPI
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

class QuoteAPI(XTPQuoteAPI):

    _contracts:dict = {} 
    _connectStatus: bool = False
    _loginStatus: bool = False
    _sub_tikers:list = []

    params = (
        ('server_ip', '127.0.0.1'),
        ('server_port', 7496),
        ('client_id', None),  # None generates a random clientid 1 -> 2^16
        ('protocol', False),
        ('_debug', False),
        ('userid', 3),  # -1 forever, 0 No, > 0 number of retries
        ('password', 3.0),  # timeout between reconnections
        ('timeoffset', True),  # Use offset to server for timestamps if needed
        ('timerefresh', 60.0),  # How often to refresh the timeoffset
        ('tiker', '688158'),  # tiker
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
        """"""
        super(XTPQuotaAPI, self).__init__()

    def OnDisconnected(self, reason) :
        """"""
        self._connectStatus = False
        self._loginStatus = False
        self.LoginServer()

    def OnError(self, error_info):
        print(error_info)


    def OnSubMarketData(self, ticker, error_info, is_last):
        pass 

    def OnUnSubMarketData(self, ticker, error_info, is_last):
        """
        退订行情应答，包括股票、指数和期权

        @remark 每条取消订阅的合约均对应一条取消订阅应答，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线
        :param ticker: 详细的合约取消订阅情况
        :param error_info: 取消订阅合约时发生错误时返回的错误信息，当error_info为空，或者error_info.error_id为0时，表明没有错误
        :param is_last: 是否此次取消订阅的最后一个应答，当为最后一个的时候为true，如果为false，表示还有其他后续消息响应
        :return:
        """
        pass

    def OnDepthMarketData(self, market_data, bid1_qty, bid1_count, max_bid1_count, ask1_qty, ask1_count, max_ask1_count):

        print(time.asctime(time.localtime(time.time())))
        print(market_data)
        # print("-------------------")
        # print(bid1_qty, bid1_count, max_bid1_count,
        #       ask1_qty, ask1_count, max_ask1_count)

    def OnQueryAllTickers(self, ticker_info, error_info, is_last):
        print(ticker_info, error_info)


    def Connect(self):
        log_level = XTPEnum.XTP_LOG_LEVEL.XTP_LOG_LEVEL_ERROR
        if self.p._debug :
            log_level = XTPEnum.XTP_LOG_LEVEL.XTP_LOG_LEVEL_TRACE
        
        if not self._connectStatus:
            self.CreateQuote(self.p.client_id, 'quota',log_level)
            self.SetHeartBeatInterval(10)
            self.LoginServer()
        else:
            print("行情接口已登录，请勿重复操作")

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

    def Close(self):
        if self._connectStatus:
            self.exit()

    def Subscrbie(self, ticker: list):
        """"""
        if self._loginStatus:
            self.SubscribeMarketData(
                ticker, XTPEnum.XTP_EXCHANGE_TYPE.XTP_EXCHANGE_UNKNOWN)


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


class XTPStore(with_metaclass(MetaSingleton, object)):
    '''Singleton class wrapping to control the connections to XTP.

    Params:

      - ``key_id`` (default:``None``): XTP API key id

      - ``secret_key`` (default: ``None``): XTP API secret key

      - ``paper`` (default: ``False``): use the paper trading environment

      - ``account_tmout`` (default: ``10.0``): refresh period for account
        value/cash refresh
    '''

    BrokerCls = None  # broker class will autoregister
    DataCls = None  # data class will auto register

    params = (
        ('key_id', ''),
        ('secret_key', ''),
        ('paper', False),
        ('usePolygon', False),
        ('account_tmout', 10.0),  # account balance refresh timeout
        ('api_version', None)
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

    def start(self, data=None, broker=None):
        pass 

    def stop(self):
        pass 

    def put_notification(self, msg, *args, **kwargs):
        self.notifs.append((msg, args, kwargs))

    def get_notifications(self):
        '''Return the pending "store" notifications'''
        self.notifs.append(None)  # put a mark / threads could still append