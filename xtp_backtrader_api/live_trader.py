import backtrader as bt
from xtpwrapper import * 
import time


class LiveTrader(TraderApi):

    def __init__(self):
        super().__init__()
        
        self.userid: str = ""
        self.password: str = ""
        self.client_id: int = 0
        self.server_ip: str = ""
        self.server_port: int = 0
        self.protocol: int = 0
        self.session_id: int = 0

        self.connect_status: bool = False
        self.login_status: bool = False

        self.sse_inited: bool = False
        self.szse_inited: bool = False

        self.order_num: int = 0
        self.trade_num: int = 0
        self.insert_order_num: int = 0 
        self.cancel_order_num: int = 0 
        self.out_count: int  = 0
        self.m_iquest_id: int = 0
        self.save_to_file_: str = ""

    
    def OnDisconnected(self, session_id, reason):
        """
        当客户端的某个连接与交易后台通信连接断开时，该方法被调用。
        @param reason 错误原因，请与错误代码表对应
        @param session_id 资金账户对应的session_id，登录时得到
        @remark 用户主动调用logout导致的断线，不会触发此函数。api不会自动重连，当断线发生时，请用户自行选择后续操作，可以在此函数中调用Login重新登录，并更新session_id，此时用户收到的数据跟断线之前是连续的

        :param session_id: 
        :param reason: 
        :return: 
        """
        pass

    def OnError(self, error_info):
        """
        错误应答

        @remark 此函数只有在服务器发生错误时才会调用，一般无需用户处理

        :param error_info: 当服务器响应发生错误时的具体的错误代码和错误信息,当error_info为空，
        或者error_info.error_id为0时，表明没有错误
        :return: 
        """
        pass

    def OnOrderEvent(self, order_info, error_info, session_id):
        """
        报单通知
        @remark 每次订单状态更新时，都会被调用，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线，在订单未成交、全部成交、全部撤单、部分撤单、已拒绝这些状态时会有响应，对于部分成交的情况，请由订单的成交回报来自行确认。所有登录了此用户的客户端都将收到此用户的订单响应

        :param order_info: 订单响应具体信息，用户可以通过order_info.
                    order_xtp_id来管理订单，通过GetClientIDByXTPID() ==
                    client_id来过滤自己的订单，order_info.qty_left字段在订单为未成交、
                    部成、全成、废单状态时，表示此订单还没有成交的数量，在部撤、全撤状态时，
                    表示此订单被撤的数量。order_info.order_cancel_xtp_id为其所对应的撤单ID，
                    不为0时表示此单被撤成功
        :param error_info: 
        :param session_id: 
        :return: 
        """
        pass

    def OnTradeEvent(self, trade_info, session_id):
        """
        成交通知
        @remark 订单有成交发生的时候，会被调用，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线。所有登录了此用户的客户端都将收到此用户的成交回报。相关订单为部成状态，需要用户通过成交回报的成交数量来确定，OnOrderEvent()不会推送部成状态。

        :param trade_info: 成交回报的具体信息，用户可以通过trade_info.order_xtp_id
                        来管理订单，通过GetClientIDByXTPID() == client_id来过滤自己的订单。对于上交所，
                        exec_id可以唯一标识一笔成交。当发现2笔成交回报拥有相同的exec_id，
                        则可以认为此笔交易自成交了。对于深交所，exec_id是唯一的，暂时无此判断机制。
                        report_index+market字段可以组成唯一标识表示成交回报。
        :param session_id: 
        :return: 
        """
        pass

    def OnCancelOrderError(self, cancel_info, error_info, session_id):
        """
        撤单出错响应
        @remark 此响应只会在撤单发生错误时被回调

        :param cancel_info: 撤单具体信息，包括撤单的order_cancel_xtp_id和待撤单的order_xtp_id
        :param error_info: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryOrder(self, order_info, error_info, request_id, is_last, session_id):
        """
        请求查询报单响应
        @remark 由于支持分时段查询，一个查询请求可能对应多个响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param order_info: 查询到的一个报单
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryTrade(self, trade_info, error_info, request_id, is_last, session_id):
        """
        请求查询成交响应
        @remark 由于支持分时段查询，一个查询请求可能对应多个响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param trade_info: 查询到的一个成交回报
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryPosition(self, position, error_info, request_id, is_last, session_id):
        """
        请求查询投资者持仓响应

        @remark 由于用户可能持有多个股票，一个查询请求可能对应多个响应，
        需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param position: 查询到的一只股票的持仓情况
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryAsset(self, asset, error_info, request_id, is_last, session_id):
        print(asset)

        """
        请求查询资金账户响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param asset: 查询到的资金账户情况
        :param error_info:
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryStructuredFund(self, fund_info, error_info, request_id, is_last, session_id):
        """
        请求查询分级基金信息响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param fund_info: 查询到的分级基金情况
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryFundTransfer(self, fund_transfer_info, error_info, request_id, is_last, session_id):
        """
        请求查询资金划拨订单响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param fund_transfer_info: 查询到的资金账户情况
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnFundTransfer(self, fund_transfer_info, error_info, session_id):
        """
        资金划拨通知

        @remark 当资金划拨订单有状态变化的时候，会被调用，需要快速返回，否则会堵塞后续消息，当堵塞严重时
        ，会触发断线。所有登录了此用户的客户端都将收到此用户的资金划拨通知。

        :param fund_transfer_info: 资金划拨通知的具体信息，用户可以通过
                                    fund_transfer_info.serial_id来管理订单，
                                    通过GetClientIDByXTPID() == client_id来过滤自己的订单。
        :param error_info: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryETF(self, etf_info, error_info, request_id, is_last, session_id):
        """
        请求查询ETF清单文件的响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param etf_info: 查询到的ETF清单文件情况
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryETFBasket(self, etf_component_info, error_info, request_id, is_last, session_id):
        """
        请求查询ETF股票篮的响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param etf_component_info: 查询到的ETF合约的相关成分股信息
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryIPOInfoList(self, ipo_info, error_info, request_id, is_last, session_id):
        """
        请求查询今日新股申购信息列表的响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        @remark 需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param ipo_info: 查询到的今日新股申购的一只股票信息
        :param error_info: 查询今日新股申购信息列表发生错误时返回的错误信息
        :param request_id: 当error_info为空，或者error_info.error_id为0时，表明没有错误
        :param is_last: 此消息响应函数是否为request_id这条请求所对应的最后一个响应，当为最后一个的时候为true，如果为false，表示还有其他后续消息响应
        :param session_id:
        :return: 
        """
        pass

    def OnQueryIPOQuotaInfo(self, quota_info, error_info, request_id, is_last, session_id):
        """
        请求查询用户新股申购额度信息的响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param quota_info: 查询到的用户某个市场的今日新股申购额度信息
        :param error_info: 查查询用户新股申购额度信息发生错误时返回的错误信息,当error_info为空，或者error_info.error_id为0时，表明没有错误
        :param request_id: 此消息响应函数对应的请求ID
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass

    def OnQueryOptionAuctionInfo(self, option_info, error_info, request_id, is_last, session_id):
        """
        请求查询期权合约的响应，需要快速返回，否则会堵塞后续消息，当堵塞严重时，会触发断线

        :param option_info: 查询到的期权合约情况
        :param error_info: 
        :param request_id: 
        :param is_last: 
        :param session_id: 
        :return: 
        """
        pass




if __name__ == '__main__':

    session_id = 0
    request_id = 1 
    test = LiveTrader() 
    test.CreateTrader(1, 'trader', xtp_enum.XTP_LOG_LEVEL.XTP_LOG_LEVEL_INFO) 

    test.SetHeartBeatInterval(10)
    test.SetSoftwareVersion("1.1.1")
    test.SetSoftwareKey('b8aa7173bba3470e390d787219b2112e')
    
    session_id = test.Login('120.27.164.69', 6001, '53191002899', '778MhWYa')
    if session_id != None and session_id != 0: 

        test.QueryAsset(session_id, 1)
        # test.Logout(int(session_id))
        # test.Release()
        print("test---", session_id)
        while(True):
            test.QueryAsset(session_id, 1)
            time.sleep(1)

        
    else:
        print(session_id, test.GetApiLastError())

    # if ret == 0:

    #     test.Logout()
    #     test.Release()
    #     # test.SubscribeAllMarketData()

    #     # print(test.OnSubscribeAllMarketData())
