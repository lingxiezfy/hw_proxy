# -*- coding: utf-8 -*-
# @Time    : 2018/9/27 18:11
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : result_server
# @Software: PyCharm

import logging
import os
import time
import configparser

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import defer
from twisted.internet import reactor, endpoints

from web_socket import WebSocketFactory


class ResultProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.proxy_connect(self)

    def lineReceived(self, line):
        self.factory.data_receive(line)

    def send_data(self, data):
        self.sendLine(data.encode())

    def connectionLost(self, reason):
        self.factory.proxy_lost()
        self.transport.loseConnection()


class ResultFactory(ServerFactory):
    protocol = ResultProtocol

    # ws ...
    factorys = {}
    mate_client = {}
    mate_result_panel = {}
    deferreds = []
    proxy_conn = None

    def __init__(self):
        self.deferreds = [self._init_result_deferred(),
                          self._init_connect_deferred(),
                          self._init_lost_deferred()]
        # 目前实现的有webSocket方式
        self.factorys["ws"] = None
        self.config = config
        self.proxy_conn = None

    def startFactory(self):
        # 注册一个 websocket 方式的结果反馈服务
        try:

            ws_port = self.config["WebSocket"]["ws_port"]
            panel_limit = int(self.config["WebSocket"]["panelLimit"])
            factory = WebSocketFactory(self.deferreds, panel_limit)
            endpoints.serverFromString(reactor, "tcp:"+ws_port).listen(factory)
            self.factorys["ws"] = factory
            logger.info("Register WebSocket Result at port %s " % ws_port)
        except Exception as e:
            print("Register webSocket Result error %s " % e.__repr__())
            self.factorys["ws"] = None

        # 其他结果反馈服务也可在此注册，按要求实现回调即可

    # receive data from proxy, just do route
    def data_receive(self, data):
        try:
            data_str = data.decode("utf-8")
            conn_type, _panel, _result = data_str.split('&', maxsplit=2)
            if '&' in _result:
                _result_s = _result.split('&')
                for _r in _result_s:
                    self.result_send_to(conn_type, self.mate_client[conn_type+"&"+_panel], _r)
            else:
                self.result_send_to(conn_type, self.mate_client[conn_type+"&"+_panel], _result)
        except Exception as e:
            logger.error("Result data error %s : %s " % (data, e.__repr__()))

    def proxy_connect(self, proxy_conn):
        logger.info("Proxy server connected")
        self.proxy_conn = proxy_conn

    def proxy_lost(self):
        logger.error("Proxy server lost ")
        self.proxy_conn = None
        for key in self.factorys:
            self.result_boadcast(key, "error:丢失代理服务器连接")
            self.factorys[key].stop_all_connect()

    # 注册窗口
    def register_panel_to_proxy(self, result_panel):
        # logger.error("register panel - %s " % result_panel)
        reactor.callLater(0.01, self.proxy_conn.send_data, "r&"+result_panel)

    # 注销窗口
    def unregister_panel_to_proxy(self, result_panel):
        # logger.error("Unregister panel - %s " % result_panel)
        reactor.callLater(0.01, self.proxy_conn.send_data, "ur&"+result_panel)

    # callback for client request register a panel
    def result_receive_from(self, client_result):
        self.deferreds[0] = self._init_result_deferred()
        client_panel = client_result[2] + "&" + client_result[0].getPeer().host + ";" + client_result[1]
        if self.is_panel_name(client_result[1]) and self.proxy_conn:
            # 更新窗口与socket的配对信息
            self.mate_client[client_panel] = client_result[0]
            self.mate_result_panel[client_result[0]] = client_panel
            # 向代理服务 注册窗口
            self.register_panel_to_proxy(client_panel)
        else:
            self.result_send_to(client_result[2], client_result[0], "error:代理服务器未连接")
            c_t_f = self.factorys[client_result[2]]
            c_t_f.stop_connect(client_result[0])
            logger.error("register panel error, proxy not found - %s " % client_panel)
            return None

    # callback for Client connect
    def result_client_connect(self, client_info):
        self.deferreds[1] = self._init_connect_deferred()
        # logger.info("Result client connected : %s " % client_info)

    # callback for Result Client lost
    def result_client_lost(self, client_info):
        self.deferreds[2] = self._init_lost_deferred()
        if self.proxy_conn:
            self.unregister_panel_to_proxy(self.mate_result_panel[client_info[0]])
            del self.mate_client[self.mate_result_panel[client_info[0]]]
            del self.mate_result_panel[client_info[0]]
        # logger.info("Result client lost: %s " % client_info)

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
    result_port = int(config["resultServer"]["result_port"])
    from twisted.internet import reactor
    port = reactor.listenTCP(result_port, factory)
    logger.info('Result Serving start on %s.' % (port.getHost(),))
    reactor.run()

logger = logging.getLogger('Result')
logger.setLevel(logging.DEBUG)
fn = os.path.split(os.path.realpath(__file__))[0] + '/log/' + str(
    time.strftime('%Y-%m-%d', time.localtime(time.time()))) + '.log'
fh = logging.FileHandler(fn, encoding='utf-8')
fh.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# ch.setFormatter(formatter)
logger.addHandler(fh)
# logger.addHandler(ch)

config = configparser.ConfigParser(delimiters='=')
config.read(os.path.split(os.path.realpath(__file__))[0] + "/config.conf", encoding="utf-8")


if __name__ == '__main__':
    main()
