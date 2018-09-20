# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 13:13
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : reactor_proxy_server
# @Software: PyCharm

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory


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


def main():

    factory = ProxyServerFactory()
    from twisted.internet import reactor
    port = reactor.listenTCP(3390, factory)
    print('Serving transforms on %s.' % (port.getHost(),))
    reactor.run()


if __name__ == '__main__':
    main()