import pytz
from datetime import datetime
import time

from xtpwrapper import QuoteAPI, TraderApi, xtp_enum, xtp_struct
import backtrader as bt


class XTPStore(QuoteAPI, bt.Store):

    BrokerCls = None  # broker class will autoregister
    DataCls = None  # data class will auto register

    _contracts:dict = {} 
    _connectStatus: bool = False
    _loginStatus: bool = False

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
        super().__init__()

    def OnDisconnected(self, reason: int) -> None:
        """"""
        self._connectStatus = False
        self._loginStatus = False
        self.LoginServer()

    def OnError(self, error_info) -> None:
        print(error_info)


    def OnSubMarketData(self, ticker, error_info, is_last):
        pass 

    def OnUnSubMarketData(self, ticker, error_info, is_last) -> None:
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



    def Connect(
        self,
    ) -> None:
        log_level = xtp_enum.XTP_LOG_LEVEL.XTP_LOG_LEVEL_ERROR
        if self.p._debug :
            log_level = xtp_enum.XTP_LOG_LEVEL.XTP_LOG_LEVEL_TRACE
        
        if not self._connectStatus:
            self.CreateQuote(self.p.client_id, 'quota',log_level)
            self.SetHeartBeatInterval(10)
            self.LoginServer()
        else:
            print("行情接口已登录，请勿重复操作")

    def LoginServer(self) -> None:
        """"""
        n = self.Login(
            self.p.server_ip,
            self.p.server_port,
            self.p.userid,
            self.p.password,
            xtp_enum.XTP_PROTOCOL_TYPE.XTP_PROTOCOL_TCP
        )

        if not n:
            self._connectStatus = True
            self._loginStatus = True
            msg = "行情服务器登录成功"
            self.QueryContract()
        else:
            msg = f"行情服务器登录失败，原因：{n}.".format(n)

        print(msg)

    def Close(self) -> None:
        """"""
        if self._connectStatus:
            self.exit()

    def Subscrbie(self, ticker: list) -> None:
        """"""
        if self._loginStatus:
            self.SubscribeMarketData(
                ticker, xtp_enum.XTP_EXCHANGE_TYPE.XTP_EXCHANGE_UNKNOWN)

    def QueryContract(self) -> None:
        """"""
        exchanges = [xtp_enum.XTP_EXCHANGE_TYPE.XTP_EXCHANGE_SH, xtp_enum.XTP_EXCHANGE_TYPE.XTP_EXCHANGE_SZ]

        for exchange_id in exchanges:
            self.QueryAllTickers(exchange_id)


if __name__ == '__main__':

    session_id = 0
    request_id = 1
    test = XTPStore(userid='53191002899', password='778MhWYa', client_id=1, server_ip='120.27.164.138', server_port=6002)
    print(XTPStore.__mro__)
    test.Connect()

    test.SubscribeMarketData(
        ['688158', '601766', '601169'], xtp_enum.XTP_EXCHANGE_TYPE.XTP_EXCHANGE_SH)

    while(True):
        time.sleep(1)

    # test.CreateQuote(1, 'quota', xtp.xtp_enum.XTP_LOG_LEVEL.XTP_LOG_LEVEL_TRACE)
    # test.SetHeartBeatInterval(10)
    # ret = test.Login('120.27.164.138', 6002, '53191002899', '778MhWYa')

    # print (ret, test.GetApiLastError())

    # if ret == 0:

    #     test.SubscribeAllMarketData(xtp.xtp_enum.XTP_EXCHANGE_TYPE.XTP_EXCHANGE_UNKNOWN)

    #     test.Logout()
    #     test.Release()
    #     print("test---", ret)
    # else:
    #     print(test.GetApiLastError())

    # if ret == 0:

    #     test.Logout()
    #     test.Release()
    #     # test.SubscribeAllMarketData()

    #     # print(test.OnSubscribeAllMarketData())
