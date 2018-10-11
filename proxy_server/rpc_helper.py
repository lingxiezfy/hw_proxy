# -*- coding: utf-8 -*-
# @Time    : 2018/8/21 22:09
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : rpc_help
# @Software: PyCharm

from xmlrpc.client import ServerProxy

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
