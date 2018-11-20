# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 14:29
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : login
# @Software: PyCharm


from twisted.web.resource import Resource
from xmlrpc.client import ServerProxy

import configparser
import os


class RPCProxy(object):
    def __init__(
            self,
            uid,
            passwd,
            dbname,
            host,
            port,
            path='object',

    ):
        self.rpc = ServerProxy('http://%s:%s/xmlrpc/%s' % (host, port, path), allow_none=True)
        self.user_id = uid
        self.passwd = passwd
        self.dbname = dbname

    def __call__(self, *request, **kwargs):
        return self.rpc.execute(self.dbname, self.user_id, self.passwd, *request, **kwargs)


class Login(Resource):

    def render_GET(self, request):
        # json_str = '{'
        # json_str += '"code":2}'
        # return json_str.encode('utf-8')
        return self.render_POST(request)

    def render_POST(self, request):
        self.real_path = os.path.split(os.path.realpath(__file__))[0]
        self.config = configparser.ConfigParser(delimiters='=')
        self.config.read(self.real_path + "/config.conf", encoding="utf-8")
        try:
            usr = request.args[b'usr'][0].decode("utf-8")
            pwd = request.args[b'pwd'][0].decode("utf-8")
            return_msg = self.login(usr, pwd)
            json_str = '{'
            if return_msg:
                json_str += '"code":1,"uid":"%s","name":"%s","usr":"%s","pwd":"%s"'\
                            % (return_msg[0], return_msg[1], usr, pwd)
            else:
                json_str += '"code":2'
            json_str += "}"
        except:
            json_str = '{'
            json_str += '"code":0}'
        return json_str.encode('utf-8')

    # 登录rpc检测
    def login(self, username, password):
        rpc_host = self.config["Odoo"]["rpc_host"]
        rpc_port = self.config["Odoo"]["rpc_port"]
        rpc_db = self.config["Odoo"]["rpc_db"]
        odoologinurl = ("http://%s:%s/xmlrpc/2/common" % (rpc_host, rpc_port))
        common = ServerProxy(odoologinurl)
        try:
            uid = common.authenticate(rpc_db, username, password, {})
        except ConnectionRefusedError as cre:
            print(" 登录失败-rpc连接失败-%s-%s-%s" % (rpc_host, rpc_port, cre.__repr__()))
            return None
        if uid:
            rpc = RPCProxy(uid, password, host=rpc_host, port=rpc_port, dbname=rpc_db)
            return_msg = rpc('res.users', 'search_read', [('id', '=', uid)], ['name'])
            name = return_msg[0].get('name')

            print(" 登录成功-用户-%s:%s" % (username, name))
            return uid, name
        else:
            print(" 登录失败-账号或密码错误-%s" % username)
            return None


resource = Login()
