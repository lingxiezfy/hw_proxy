# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 18:11
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : result_server
# @Software: PyCharm

import struct

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import defer
from twisted.internet import reactor, endpoints

from web_socket import WebSocketFactory


class ResultProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.proxy_connect(self)
        # print("发现代理数据连接：%s" % (self.transport.getPeer(),))

    def lineReceived(self, line):
        self.factory.data_receive(line)

    def send_data(self, data):
        self.sendLine(data.encode())

    def connectionLost(self, reason):
        self.factory.proxy_lost()
        print("代理连接丢失：%s" % (self.transport.getPeer(),))
        self.transport.loseConnection()


class ResultFactory(ServerFactory):
    protocol = ResultProtocol

    # ws ...
    factorys = {}
    result_panel_mate = {}
    mate_result_panel = {}
    deferreds = []
    proxy_conn = None

    def __init__(self):
        self.deferreds = [self._init_result_deferred(),
                          self._init_connect_deferred(),
                          self._init_lost_deferred()]
        # 目前实现的有webSocket方式
        self.factorys["ws"] = None
        self.proxy_conn = None

    def startFactory(self):
        # 注册一个 websocket 方式的结果反馈服务
        try:
            print("Register webSocket Result at port 6677")
            factory = WebSocketFactory(self.deferreds, 4)
            endpoints.serverFromString(reactor, "tcp:6677").listen(factory)
            self.factorys["ws"] = factory
        except Exception as e:
            print("Register webSocket Result error %s " % e.__repr__())
            self.factorys["ws"] = None

        # 其他结果反馈服务也可在此注册，按要求实现回调即可

    # receive data from proxy, just do route
    def data_receive(self, data):
        try:
            data_str = data.decode("utf-8")
            conn_type, _panel, _result = data_str.split('&', maxsplit=2)
            self.result_send_to(conn_type, self.result_panel_mate[_panel], _result)
        except Exception as e:
            print("result error %s " % data)
            print(e.__repr__())

    def proxy_connect(self, proxy_conn):
        print("proxy connected %s " % proxy_conn)
        self.proxy_conn = proxy_conn

    def proxy_lost(self):
        print("proxy lost, waiting for reconnect")
        self.proxy_conn = None

    # 注册窗口
    def register_panel_to_proxy(self, _type, result_panel):
        if self.proxy_conn:
            reactor.callLater(0.01, self.proxy_conn.send_data, _type+"&r&"+result_panel)
        else:
            print("proxy not found")

    # 注销窗口
    def unregister_panel_to_proxy(self, _type, result_panel):
        if self.proxy_conn:
            reactor.callLater(0.01, self.proxy_conn.send_data, _type+"&ur&"+result_panel)
        else:
            print("proxy not found")

    # callback for client request register a panel
    def result_receive_from(self, client_result):
        self.deferreds[0] = self._init_result_deferred()
        print("pull factory %s : %s" % (client_result[0], client_result[1]))
        if self.is_panel_name(client_result[1]):
            client_panel = client_result[0].getPeer().host+";"+client_result[1]
            # 更新窗口与socket的配对信息
            self.result_panel_mate[client_panel] = client_result[0]
            self.mate_result_panel[client_result[0]] = client_panel
            # 向代理服务 注册窗口
            self.register_panel_to_proxy(client_result[2], client_panel)
        else:
            return None

    # callback for Client connect
    def result_client_connect(self, client_info):
        self.deferreds[1] = self._init_connect_deferred()
        print("client connected : %s ", client_info)

    # callback for Result Client lost
    def result_client_lost(self, client_info):
        self.deferreds[2] = self._init_lost_deferred()
        self.unregister_panel_to_proxy(client_info[1], self.mate_result_panel[client_info[0]])
        del self.mate_result_panel[client_info[0]]
        print("client lost: %s ", client_info)

    # result can't encode,it should be a str,not bytes
    def result_boadcast_local(self, conn_type, clients, result):
        if conn_type in self.factorys:
            c_t_f = self.factorys[conn_type]
            if c_t_f:
                c_t_f.boadcast_local(clients, result)
        else:
            raise KeyError(" %s not register " % conn_type)

    # result can't encode,it should be a str,not bytes
    def result_boadcast(self, conn_type, result):
        if conn_type in self.factorys:
            c_t_f = self.factorys[conn_type]
            if c_t_f:
                c_t_f.boadcast(result)
        else:
            raise KeyError(" %s not register " % conn_type)

    # result can't encode,it should be a str
    def result_send_to(self, conn_type, client, result):
        if conn_type in self.factorys:
            c_t_f = self.factorys[conn_type]
            if c_t_f:
                c_t_f.send_to(client, result)
        else:
            raise KeyError(" %s not register " % conn_type)

    # judge mate info from client is a panel or not
    def is_panel_name(self, _panel):
        if "panel" in _panel:
            return True
        else:
            return False

    def _init_connect_deferred(self):
        d = defer.Deferred()
        d.addBoth(self.result_client_connect)
        return d

    def _init_lost_deferred(self):
        d = defer.Deferred()
        d.addBoth(self.result_client_lost)
        return d

    def _init_result_deferred(self):
        d = defer.Deferred()
        d.addBoth(self.result_receive_from)
        return d


def main():
    factory = ResultFactory()
    from twisted.internet import reactor
    port = reactor.listenTCP(6690, factory)
    print('Result Serving transforms on %s.' % (port.getHost(),))
    reactor.run()


if __name__ == '__main__':
    main()
