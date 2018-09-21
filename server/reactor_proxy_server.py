# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 13:13
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : reactor_proxy_server
# @Software: PyCharm

from twisted.protocols.basic import LineReceiver
from twisted.internet import defer,main
from twisted.internet.protocol import ServerFactory, ReconnectingClientFactory
from twisted.internet import reactor

# 代理传输协议，基于LineReceiver
class ProxyProtocol(LineReceiver):
    def connectionMade(self):
        print("客户端连接：%s" % (self.transport.getPeer(),))

    def lineReceived(self, line):
        self._on_data_received(line)

    def _on_data_received(self, data):
        print(data)
        print(data.decode())
        pass

    # 连接丢失时的回调
    def connectionLost(self, reason):
        print("连接丢失：%s" % (self.transport.getPeer(),))
        self.transport.loseConnection()
        pass


# 代理服务工厂，管理客户端连接
class ProxyServerFactory(ServerFactory):
    # 注册一个传输协议
    protocol = ProxyProtocol
    result_protocol = None
    deferred = []

    def __init__(self):
        self.deferred = [self._init_set_deferred(), self._init_lost_deferred()]
        print("create %s" % self.deferred)

    def startFactory(self):
        result_factory = ResultClientFactory(self.deferred)
        reactor.connectTCP("127.0.0.1", 6690, result_factory)

    def _init_set_deferred(self):
        d = defer.Deferred()
        d.addCallbacks(self.set_result_protocol, self.set_result_failed)
        return d

    def _init_lost_deferred(self):
        d = defer.Deferred()
        d.addBoth(self.on_result_protocol_lost)
        return d

    def set_result_protocol(self, p):
        self.deferred[0] = self._init_set_deferred()
        self.result_protocol = p
        print("Set result protocol Success：%s" % self.result_protocol)
        self.send_result("test")

    def set_result_failed(self, err):
        self.deferred[0] = self._init_set_deferred()
        print("Set result protocol failure：%s" % err)

    def on_result_protocol_lost(self, err):
        self.deferred[1] = self._init_lost_deferred()
        print("Lost result protocol: %s" % err)
        self.result_protocol = None

    def send_result(self, result):
        reactor.callLater(0.1, self.result_protocol.send_result, result)


# 与ResultWebSocketServer通信Protocol
class ResultClientProtocol(LineReceiver):

    def __init__(self, deferred):
        self.deferred = deferred

    def connectionMade(self):
        self.deferred.callback(self)
        print("Connected to Result Server and callback to set protocol")

    def send_result(self, result):
        print("send %s" % self.deferred)
        self.sendLine(result.encode())
        self.connectionLost()

    def connectionLost(self, reason=main.CONNECTION_LOST):
        self.transport.loseConnection()


# 与ResultWebSocketServer通信Factory
class ResultClientFactory(ReconnectingClientFactory):
    p = None

    def __init__(self, deferred):
        self.deferred = deferred

    def buildProtocol(self, addr):
        self.p = ResultClientProtocol(self.deferred[0])
        self.p.factory = self
        self.resetDelay()
        print("Making result protocol ...")
        return self.p

    def clientConnectionFailed(self, connector, reason):
        print("Connect to result server failure")
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, unused_reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, unused_reason)
        print("Lost Connection from result server")
        self.deferred[1].errback(unused_reason)



def main():

    factory = ProxyServerFactory()
    port = reactor.listenTCP(3390, factory)
    print('Proxy Serving transforms on port %d' % port.getHost().port)
    # from twisted.internet.address import IPv4Address
    reactor.run()


if __name__ == '__main__':
    main()