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


# {"code":1,"uid":"32","name":"wh004","usr":"wh004","pwd":"wh004"}
# out_sourcing_pick_scan.rpy?uid=32&pwd=wh004&job_num=0001119727
class OutSourcingPickScan(Resource):

    def render_POST(self, request):
        session = request.getSession()
        try:
            config = IConfig(session)
            rpc_host = config.config["Odoo"]["rpc_host"]
            rpc_port = config.config["Odoo"]["rpc_port"]
            rpc_db = config.config["Odoo"]["rpc_db"]
            PickType = config.config['OutSourcingPickScan']['PickType']
            uid = int(request.args[b'uid'][0].decode("utf-8"))
            pwd = request.args[b'pwd'][0].decode("utf-8")
            job_num = request.args[b'job_num'][0].decode("utf-8")
            rpc = RPCProxy(uid, pwd, host=rpc_host, port=rpc_port, dbname=rpc_db)
            msg = ""
            msg_type = ""
            if config.config.getboolean("OutSourcingPickScan", "IsLot"):
                config.logger.error(" 执行批次isLot:True - %s" % job_num)
                # 获取生产单(制造单)
                ids = rpc("mrp.production", "search", [("state", "not in", ["cancel", "done"]),
                                                       ["restrict_lot_id.name", "=", job_num]])
                # 获取采购单
                if ids:
                    PurchaseOrderRecords = rpc("purchase.order", "search_read", [("mo_id.id", "=", ids[0])], ["name"])
                    if PurchaseOrderRecords:
                        purchaseordername = PurchaseOrderRecords[0]['name']
                        config.logger.info(" 获取采购单成功 - %s:%s" % (job_num, purchaseordername))
                    else:
                        msg = job_num + " :无外协信息,请联系主管,确认采购询价单"
                        msg_type = "error"
                        config.logger.error(" 获取采购单失败 - %s" % job_num)
                else:
                    msg = job_num + " :无外协信息,请联系主管,确认制造单"
                    msg_type = "error"
                    config.logger.error(" 获取生产单(制造单)失败 - %s" % job_num)
            else:
                config.logger.info(" 跳过批次isLot:False - %s" % job_num)
                purchaseordername = job_num

            if not msg_type:
                # 获取分拣类型
                pickids = rpc("stock.picking.type", "search", [("name", "=", PickType)])
                if pickids:
                    MoveRecords = rpc("stock.picking", "search_read",
                                      [("state", "not in", ["cancel"]),
                                       ("origin", "=", purchaseordername),
                                       ("picking_type_id", "=", pickids[0])], ["id"])
                    if MoveRecords:
                        mr_id = MoveRecords[0]['id']
                        strSucceed = rpc("stock.picking", "action_done_remote", mr_id)
                        if strSucceed == "success!":
                            msg = job_num + " 来料接收:操作成功 - 执行出库:"

                            config.logger.info(" %s" % msg)
                            returnmsg = rpc('mrp.production', 'rpc_action_picking_done', job_num, 'lens')
                            if returnmsg != '100':
                                if returnmsg == "501":
                                    returnmsg = "镜片已出库"
                                if returnmsg == "502":
                                    returnmsg = "镜架已出库"
                                elif returnmsg == "503":
                                    returnmsg = "无库存"
                                elif returnmsg == "504":
                                    returnmsg = "保留异常"
                                elif returnmsg == "505":
                                    returnmsg = "出库动作异常"
                                elif returnmsg == "506":
                                    returnmsg = "出库单不存在"
                                elif returnmsg == "507":
                                    returnmsg = "生产单不存在"
                                elif returnmsg == "508":
                                    returnmsg = "不需要出库"
                                msg += returnmsg+" - 请手动出库"
                                msg_type = 'warning'
                            else:
                                returnmsg = "出库成功"
                                msg += returnmsg
                                msg_type = 'info'
                        else:
                            msg = job_num + " 来料接收:操作失败 : " + strSucceed
                            msg_type = 'error'
                            config.logger.error(" %s" % msg)
                    else:
                        msg = job_num + " :无外协信息,请联系主管,确认制造单或采购询价单"
                        msg_type = 'error'
                        config.logger.error(" 无外协信息 - %s" % job_num)
                else:
                    msg = job_num + " :无分拣类型,请联系主管,确认分拣类型: "+PickType
                    msg_type = 'error'
                    config.logger.error(" 无分拣类型 - %s" % PickType)

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
