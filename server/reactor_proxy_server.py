# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 13:13
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : reactor_proxy_server
# @Software: PyCharm

from twisted.protocols.basic import LineReceiver
from twisted.internet import defer, main
from twisted.python.failure import Failure
from twisted.internet.protocol import ServerFactory, ReconnectingClientFactory
from twisted.internet import reactor

# 代理传输协议，基于LineReceiver
class ProxyProtocol(LineReceiver):
    def connectionMade(self):
        print("客户端连接：%s" % (self.transport.getPeer(),))

    def lineReceived(self, line):
        self._on_data_received(line)

    def _on_data_received(self, data):
        print(data.decode())
        self.factory.data_receive(data.decode())

    # 连接丢失时的回调
    def connectionLost(self, reason):
        print("连接丢失：%s" % (self.transport.getPeer(),))
        self.transport.loseConnection()
        pass


# 代理服务工厂，管理客户端连接 与 结果反馈
class ProxyServerFactory(ServerFactory):
    # 注册一个传输协议
    protocol = ProxyProtocol
    result_protocol = None
    deferred = []

    def __init__(self):
        self.deferred = [self._init_set_deferred(), self._init_lost_deferred(), self._init_result_info_deferred()]
        print("create %s" % self.deferred)

    def startFactory(self):
        result_factory = ResultClientFactory(self.deferred)
        reactor.connectTCP("127.0.0.1", 6690, result_factory)

    def data_receive(self, data):
        self.send_result(data)

    def on_result_info_receive(self, data):
        self.deferred[2] = self._init_result_info_deferred()
        print(data)
        pass

    def _init_set_deferred(self):
        d = defer.Deferred()
        d.addCallbacks(self.set_result_protocol, self.set_result_failed)
        return d

    def _init_lost_deferred(self):
        d = defer.Deferred()
        d.addBoth(self.on_result_protocol_lost)
        return d

    def _init_result_info_deferred(self):
        d = defer.Deferred()
        d.addBoth(self.on_result_info_receive)
        return d

    def set_result_protocol(self, p):
        self.deferred[0] = self._init_set_deferred()
        self.result_protocol = p
        print("Set result protocol Success：%s" % self.result_protocol)
        self.send_result("ws&127.0.0.1;mate_panel_1&echo")

    def set_result_failed(self, err):
        self.deferred[0] = self._init_set_deferred()
        print("Set result protocol failure：%s" % err)

    def on_result_protocol_lost(self, err):
        self.deferred[1] = self._init_lost_deferred()
        print("Lost result protocol: %s" % err)
        self.result_protocol = None

    def send_result(self, result):
        if self.result_protocol is None:
            print("Result server have not connect")
        else:
            reactor.callLater(0.01, self.result_protocol.send_result, result)


# 与ResultServer通信Protocol
class ResultClientProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.connect_success(self)

    def lineReceived(self, line):
        self.factory.data_receive(line)

    def send_result(self, result):
        self.sendLine(result.encode())

    def connectionLost(self, reason=main.CONNECTION_LOST):
        self.transport.loseConnection()


# 与ResultServer通信Factory
class ResultClientFactory(ReconnectingClientFactory):
    p = None

    def __init__(self, deferred):
        self.deferred = deferred

    def buildProtocol(self, addr):
        self.p = ResultClientProtocol()
        self.p.factory = self
        self.resetDelay()
        print("Making result protocol ...")
        return self.p

    def data_receive(self, data):
        self.deferred[2].callback(data)

    def connect_success(self, p):
        self.deferred[0].callback(p)
        print("Connected to Result Server and callback to set protocol")

    def clientConnectionFailed(self, connector, reason):
        print("Connect to result server failure, waiting for reconnect...")
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, unused_reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, unused_reason)
        print("Lost Connection from result server, waiting for reconnect...")
        self.deferred[1].errback(unused_reason)



def main():

    factory = ProxyServerFactory()
    port = reactor.listenTCP(3390, factory)
    print('Proxy Serving transforms on port %d' % port.getHost().port)
    # from twisted.internet.address import IPv4Address
    reactor.run()


if __name__ == '__main__':
    main()