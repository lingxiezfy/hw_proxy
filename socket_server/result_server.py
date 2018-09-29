# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 18:11
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : result_server
# @Software: PyCharm


from twisted.internet.protocol import ServerFactory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import main, error, defer
from twisted.python import failure
from twisted.internet import reactor, endpoints

from web_socket import WebSocketFactory


class ResultProtocol(LineReceiver):

    def connectionMade(self):
        print("发现连接：%s" % (self.transport.getPeer(),))

    def lineReceived(self, line):
        self.factory.data_receive(line)

    # 连接丢失时的回调
    def connectionLost(self, reason):
        print("连接丢失：%s" % (self.transport.getPeer(),))
        self.transport.loseConnection()


class ResultFactory(ServerFactory):
    protocol = ResultProtocol
    web_factory = None
    web_deferreds = []

    def __init__(self):
        self.web_deferreds = [self._init_web_result_deferred(), ]

    def startFactory(self):
        print("open webSocket at port 6677")
        self.web_factory = WebSocketFactory(self.web_deferreds)
        endpoints.serverFromString(reactor, "tcp:6677").listen(self.web_factory)

    # callback for WebSocket result
    def result_receive_from(self, client_result):
        self.web_deferreds[0] = self._init_web_result_deferred()
        print("pull factory %s : %s" % (client_result[0], client_result[1]))

    def _init_web_result_deferred(self):
        d = defer.Deferred()
        d.addBoth(self.result_receive_from)
        return d

    # receive data from proxy
    def data_receive(self, data):
        pass

    # result can't encode,it should be a str,not bytes
    def result_boadcast(self, result):
        if self.web_factory:
            self.web_factory.boadcast(result)

    # result can't encode,it should be a str
    def result_send_to(self, client, result):
        if self.web_factory:
            self.web_factory.send_to(client, result)


def main():
    factory = ResultFactory()
    from twisted.internet import reactor
    port = reactor.listenTCP(6690, factory)
    print('Result Serving transforms on %s.' % (port.getHost(),))
    reactor.run()


if __name__ == '__main__':
    main()
