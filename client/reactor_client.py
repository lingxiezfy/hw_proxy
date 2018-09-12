# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 16:54
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : reactor_client
# @Software: PyCharm

from twisted.protocols.basic import LineReceiver
from twisted.protocols.basic import NetstringReceiver
from twisted.internet.protocol import ClientFactory


class ProxyProtocol(NetstringReceiver):
    def connectionMade(self):
        self.sendString("I'm connecting!".encode())
        # self.sendLine("I'm connecting!".encode())

    def send_some_thing(self):
        self.sendLine("I send number!".encode())


class HidClientFactory(ClientFactory):
    protocol = ProxyProtocol
    proto = None

    def buildProtocol(self, addr):
        p = ClientFactory.buildProtocol(self, addr)
        self.proto = p
        return p


def send_loop(factory):
    print("send")
    factory.proto.send_some_thing("I send number!")


def proxy_main():
    factory = HidClientFactory()
    from twisted.internet import reactor
    reactor.connectTCP('192.168.1.139', 3390, factory)
    reactor.run()
    # reactor.callWhenRunning(send_loop, factory)


if __name__ == "__main__":
    proxy_main()
