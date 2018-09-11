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
    def dataReceived(self, data):
        self._on_data_received(data)

    def _on_data_received(self, data):
        print(data.decode())
        pass

    # 连接丢失时的回调
    def connectionLost(self):
        print("连接丢失：%s" % self.transport.getHost())
        self.transport.loseConnection()
        pass


# 代理服务工厂，管理客户端连接
class ProxyServerFactory(ServerFactory):
    # 注册一个传输协议
    protocol = ProxyProtocol


def main():

    factory = ProxyServerFactory()
    from twisted.internet import reactor
    port = reactor.listenTCP(3390, factory, interface='192.168.1.139')
    print('Serving transforms on %s.' % (port.getHost(),))
    reactor.run()


if __name__ == '__main__':
    main()