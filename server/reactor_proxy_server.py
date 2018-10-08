# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 13:13
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : reactor_proxy_server
# @Software: PyCharm

from twisted.protocols.basic import LineReceiver
from twisted.internet import defer, main
from twisted.internet.protocol import ServerFactory, ReconnectingClientFactory
from twisted.internet import reactor

import struct
import configparser


# 代理传输协议，基于LineReceiver
class ProxyProtocol(LineReceiver):
    peer_ip = ""

    def connectionMade(self):
        self.peer_ip = self.transport.getPeer().host
        print("客户端连接：%s" % (self.transport.getPeer(),))

    def lineReceived(self, line):
        self._on_data_received(self.peer_ip, line)

    def _on_data_received(self, peer_ip, data):
        self.factory.data_receive(peer_ip, data)

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

    output_panel = {}
    config = None

    def __init__(self):
        self.deferred = [self._init_set_deferred(), self._init_lost_deferred(), self._init_result_info_deferred()]
        self.config = configparser.ConfigParser(delimiters='=')
        self.config.read("config.conf")
        print("create %s" % self.deferred)

    def startFactory(self):
        result_factory = ResultClientFactory(self.deferred)
        reactor.connectTCP("127.0.0.1", 6690, result_factory)

    def data_receive(self, peer_ip, data):
        try:
            _type, _source, _keys = struct.unpack("3s60s20s", data)
            input_type = _type.decode("utf-8").rstrip('\0')
            input_source = _source.decode("utf-8").rstrip('\0')
            input_keys = _keys.decode("utf-8").rstrip('\0')

            input_path = peer_ip+"&"+input_source

            if self.config.has_option(peer_ip, input_path):
                o = self.config[peer_ip][input_path]
                if o == '#':
                    print("It isn't set panel to show : %s " % input_path)
                elif o in self.output_panel:
                    msg = self.deal_data(input_path, input_keys)
                    self.send_msg_to(o, msg)
                else:
                    print("panel %s is not use: %s " % (o, input_keys))
            else:
                print("new Path input : %s " % input_path)

                if self.config.has_section(peer_ip):
                    self.config[peer_ip][input_path] = "#"
                else:
                    self.config[peer_ip] = {}
                    self.config[peer_ip][input_path] = "#"

                with open('config.conf', 'w') as configfile:
                    self.config.write(configfile)
        except Exception as e:
            print(e.__repr__())
            pass

    def send_msg_to(self, target, msg):
        self.send_result(target+"&"+msg)

    login_recode = {}
    state_recode = {}
    num_recode = {}

    def is_login_value(self, value):
        if value == "G18206":
            return True
        else:
            return False

    def is_state_value(self, value):
        if value == "FCTEST":
            return True
        else:
            return False

    def deal_data(self, _path, _data):
        login_value = self.login_recode.get(_path, None)
        if self.is_login_value(_data):
            self.login_recode[_path] = _data
            self.num_recode[_path] = 0
            self.state_recode[_path] = None
            return "login:张凤育:%s&num:0&state: &cls:1&msg:登录成功" % _data
        elif self.is_state_value(_data):
            if login_value:
                self.state_recode[_path] = _data
                self.num_recode[_path] = 0
                return "state:%s&num:0&cls:1&msg:设置状态成功" % _data
            else:
                return "error:未登录"
        else:
            state_value = self.state_recode.get(_path, None)
            if login_value is None:
                return "error:未登录"
            elif state_value is None:
                return "error:未设置状态"
            else:
                self.num_recode[_path] += 1
                return "login:张凤育:%s&state:%s&num:%d&msg:%s" % (login_value, state_value, self.num_recode[_path], _data)

    def on_result_info_receive(self, data):
        self.deferred[2] = self._init_result_info_deferred()
        try:
            _result_type, _op, _panel = data.split('&', maxsplit=2)
            if _op == 'r':
                self.output_panel[_result_type+"&"+_panel] = []
                # self.output_panel_list.append(_result_type+"&"+_panel)
                print("register : %s" % _result_type+"&"+_panel)
            elif _op == 'ur':
                del self.output_panel[_result_type+"&"+_panel]
                print(" un register : %s" % _result_type + "&" + _panel)
            else:
                raise Exception("error op : %s " % _op)
        except Exception as e:
            print("result panel error %s " % e.__repr__())

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
        # print("Set result protocol Success：%s" % self.result_protocol)

    def set_result_failed(self, err):
        self.deferred[0] = self._init_set_deferred()
        # print("Set result protocol failure：%s" % err)

    def on_result_protocol_lost(self, err):
        self.deferred[1] = self._init_lost_deferred()
        # print("Lost result protocol: %s" % err)
        self.result_protocol = None

    def send_result(self, result):
        if self.result_protocol is None:
            print("Result server is not connect")
            pass
        else:
            reactor.callLater(0.01, self.result_protocol.send_result, result)


# 与ResultServer通信Protocol
class ResultClientProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.connect_success(self)

    def lineReceived(self, line):
        self.factory.data_receive(line.decode())

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