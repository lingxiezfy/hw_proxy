# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 16:26
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : dofault.rpy
# @Software: PyCharm

from twisted.web.resource import Resource
from xmlrpc.client import ServerProxy

import os
import configparser
import json
import time
import traceback


# 当系统前时间
def now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class DoFault(Resource):

    def __init__(self):
        super(DoFault, self).__init__()
        self.real_path = os.path.split(os.path.realpath(__file__))[0]
        self.config = configparser.ConfigParser(delimiters='=')

    def render_GET(self, request):
        return self.render_POST(request)

    def render_POST(self, request):
        try:
            self.config.read(self.real_path + "/config.conf", encoding="utf-8")
            rpc_host = self.config["Odoo"]["rpc_host"]
            rpc_port = self.config["Odoo"]["rpc_port"]
            rpc_db = self.config["Odoo"]["rpc_db"]
            uid = int(request.args[b'uid'][0].decode("utf-8"))
            pwd = request.args[b'pwd'][0].decode("utf-8")

            job_num = request.args[b'job_num'][0].decode("utf-8")
            break_type = request.args[b'break_type'][0].decode("utf-8")
            break_reason = request.args[b'break_reason'][0].decode("utf-8")
            falut_data = {
                'tracking_number': job_num,
                'worker_center_id': self.config['worker_center'][break_reason[0:1]],
                'location_id': "Waiting To Production",
                'scrap_location_id': "Scrap In C" if break_type == 'S' else "Bad In C",
                'scrap_type': request.args[b'break_part'][0].decode("utf-8"),
                'scrap_fault_cause_id': break_reason[1:],
                'scrap_action_id': break_type,
                'qty': '1'
            }
            json_fault_data = json.dumps(falut_data)
            try:
                rpc = RPCProxy(uid, pwd, host=rpc_host, port=rpc_port, dbname=rpc_db)
                result = rpc('mrp.workorder', 'do_scrap_production_new', json_fault_data)
                if 'success' in result:
                    msg = result.split('-')[0] + '--' + job_num + '  操作成功！'
                    msg_type = 'info'
                elif '400' in result:
                    msg = '未领料不能报损！--' + job_num + '  操作失败！'
                    msg_type = 'error'
                elif 'no stock' in result:
                    msg = '库存不足！--' + job_num + '  操作失败！'
                    msg_type = 'error'
                else:
                    msg = '单号有误' + result + '--' + job_num + '  操作失败！'
                    msg_type = 'error'
            except:
                print(traceback.print_exc())
                msg = '连接失败，请重试！--' + job_num + '  操作失败！'
                msg_type = 'error'
            json_str = '{'
            json_str += '"code":1,"time":"%s","msg":"%s","msg_type":"%s"' % (now_time(), msg, msg_type)
            json_str += '}'
        except:
            print(traceback.print_exc())
            json_str = '{"code":0}'
        return json_str.encode('utf-8')


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


resource = DoFault()
