# -*- coding: utf-8 -*-
# @Time    : 2018/9/20 15:19
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : web_socket_server
# @Software: PyCharm
from twisted.internet import reactor
from twisted.internet.protocol import Protocol,Factory
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.web import resource, server


class ResultProtocol(LineReceiver):

    def connectionMade(self):
        print("发现连接：%s" % (self.transport.getPeer(),))

    def lineReceived(self, line):
        self._on_result_receive(line)

    def _on_result_receive(self, result):
        # print(result)
        print(result.decode())

    # 连接丢失时的回调
    def connectionLost(self, reason):
        print("连接丢失：%s" % (self.transport.getPeer(),))
        self.transport.loseConnection()


class ResultFactory(ServerFactory):
    protocol = ResultProtocol
    def startFactory(self):
        print("开启webSocket")


def main():

    factory = ResultFactory()
    from twisted.internet import reactor
    port = reactor.listenTCP(6690, factory)
    print('Serving transforms on %s.' % (port.getHost(),))
    reactor.run()


if __name__ == '__main__':
    main()