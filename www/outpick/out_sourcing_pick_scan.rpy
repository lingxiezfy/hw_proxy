# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 13:52
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : out_sourcing_pick_scan
# @Software: PyCharm

cache()

from zope.interface import Interface, Attribute
from twisted.web.resource import Resource
from xmlrpc.client import ServerProxy

import time


class IConfig(Interface):
    real_path = Attribute("environment real path.")
    config = Attribute("An config file.")
    logger = Attribute("log obj")


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


# 当系统前时间
def now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class OutSourcingPickScan(Resource):

    def render_POST(self, request):
        session = request.getSession()
        try:
            config = IConfig(session)
            rpc_host = config.config["Odoo"]["rpc_host"]
            rpc_port = config.config["Odoo"]["rpc_port"]
            rpc_db = config.config["Odoo"]["rpc_db"]
            uid = int(request.args[b'uid'][0].decode("utf-8"))
            pwd = request.args[b'pwd'][0].decode("utf-8")
            job_num = request.args[b'job_num'][0].decode("utf-8")
            try:
                rpc = RPCProxy(uid, pwd, host=rpc_host, port=rpc_port, dbname=rpc_db)
                config.logger.error(" 执行批次 - %s" % job_num)
                # 获取生产单(制造单)
                ids = rpc("mrp.production", "search", [("state", "not in", ["cancel", "done"]),
                                                       ["restrict_lot_id.name", "=", job_num]])
                # 获取采购单
                if ids:
                    PurchaseOrderRecords = rpc("purchase.order", "search_read", [("mo_id.id", "=", ids[0])], ["name"])
                    if PurchaseOrderRecords:
                        PickingTypeName = config.config['OutSourcingPickScan']['PickingTypeName']
                        strSucceed = rpc("stock.picking", "action_done_remote2", job_num, PickingTypeName)
                        if strSucceed == "success!":
                            msg = job_num + " 来料接收:操作成功"
                            msg_type = 'info'
                            config.logger.info(" %s" % msg)
                        else:
                            msg = job_num + " 来料接收:操作失败 : " + strSucceed
                            msg_type = 'error'
                            config.logger.error(" %s" % msg)
                    else:
                        msg = job_num + " :无外协信息,请联系主管,确认采购询价单"
                        msg_type = "error"
                        config.logger.error(" 获取采购单失败 - %s" % job_num)
                else:
                    msg = job_num + " :无外协信息,请联系主管,确认制造单"
                    msg_type = "error"
                    config.logger.error(" 获取生产单(制造单)失败 - %s" % job_num)
            except:
                msg = job_num + " :连接服务器失败，请重试！"
                msg_type = "error"
                config.logger.error(" 连接服务器失败 - %s" % job_num)

            json_str = '{'
            json_str += '"code":1,"time":"%s","msg":"%s","msg_type":"%s"' % (now_time(), msg, msg_type)
            json_str += '}'
        except TypeError:
            json_str = '{'
            json_str += '"code":2}'
        except:
            json_str = '{'
            json_str += '"code":0}'

        return json_str.encode('utf-8')


resource = OutSourcingPickScan()
