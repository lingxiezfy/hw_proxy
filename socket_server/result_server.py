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
import hashlib
import base64
import struct
from twisted.web.http import HTTPFactory, HTTPChannel, _GenericHTTPChannelProtocol

from web_socket import WebSocketProtocol

class ResultServerFactory(HTTPFactory):
    # protocol = _genericHttpChannelProtocol
    protocol = WebSocketProtocol


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

    def startFactory(self):
        print("open webSocket at port 6677")
        factory = ResultServerFactory()
        endpoints.serverFromString(reactor, "tcp:6677").listen(factory)

    def data_receive(self, data):
        print(data)


def main():
    factory = ResultFactory()
    from twisted.internet import reactor
    port = reactor.listenTCP(6690, factory)
    print('Result Serving transforms on %s.' % (port.getHost(),))
    reactor.run()


if __name__ == '__main__':
    main()
