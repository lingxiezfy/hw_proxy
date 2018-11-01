# -*- coding: utf-8 -*-
# @Time    : 2018/10/29 16:09
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : scan_config
# @Software: PyCharm
from twisted.web.resource import Resource
import configparser
import os


class scan_config_resource(Resource):
    def render_GET(self, request):
        return self.render_POST(request)

    def render_POST(self, request):
        real_path = os.path.split(os.path.realpath(__file__))[0]
        config = configparser.ConfigParser(delimiters='=')
        config.read(real_path + "/config.conf", encoding="utf-8")
        view_ip = request.getClientIP()
        if config.has_option('PanelLimit', view_ip):
            panel_limit = config['PanelLimit'][view_ip]
        else:
            panel_limit = ""
        if panel_limit:
            limit_num = panel_limit
        else:
            limit_num = '1'
        json_str = b'{"panel_limit":'+limit_num.encode()\
                   + b',"min_width":' + config['SizeRange']['min_width'].encode() \
                   + b',"min_width":' + config['SizeRange']['min_width'].encode() \
                   + b',"ws_host":"' + config['WebSocket']['ws_host'].encode() \
                   + b'","ws_port":' + config['WebSocket']['ws_port'].encode() + b'}'
        return json_str


resource = scan_config_resource()
