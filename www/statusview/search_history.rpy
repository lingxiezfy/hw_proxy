# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:21
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : search_history
# @Software: PyCharm

import psycopg2
from twisted.web.resource import Resource
import json
import datetime


class SqlService():
    def __init__(self, util, host, port, user, pwd, db):
        self.util = util
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.port = port

    def __GetConnect(self):
        if not self.db:
            raise (NameError, "没有设置数据库信息")
        self.conn = self.util.connect(
            host=self.host, port=self.port, user=self.user, password=self.pwd, database=self.db)
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "连接失败")
        else:
            return cur

    def ExecForCursor(self,sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        return cur

    def ExecQuery(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        data = cur.fetchall()
        row = cur.fetchone()
        rows = cur.fetchmany(10)

        return data

    def ExecNonQuery(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()

    def CloseDB(self):
        self.conn.close()


class order_list_resource(Resource):
    def render_GET(self, request):
        self.render_POST(request)

    def UTF_time(self,time_obj):
        eight_hour = datetime.timedelta(hours=8)
        return time_obj+eight_hour

    def render_POST(self, request):

        host = '106.14.239.39'
        port = 5432
        user = 'odoo'
        pwd = 'trioo258'
        database = 'gno'
        try:
            job_num = request.args[b'job_num'][0].decode("utf-8")
        except:
            print("非法访问")
        sql = "SELECT mwfr.job_num,mwfr.description,mwfr.operate_time,rp.name \"operator\",rr.name \"deptment\", mwfr.matter,mwfr.state from (( " \
        "SELECT mwf.*,mw.resource_id,res_users.partner_id from (SELECT job_num,description,operate_time,operator,deptment,matter,state from mrp_work_flow_history WHERE job_num = '%s') mwf "\
		"LEFT JOIN mrp_workcenter mw on mwf.deptment = mw.id LEFT JOIN res_users on  mwf.operator = res_users.id "\
	    ") mwfr LEFT JOIN (SELECT resource_resource.id,resource_resource.name FROM resource_resource) rr on mwfr.resource_id = rr.id "\
		"LEFT JOIN (SELECT res_partner.id,res_partner.name FROM res_partner) rp on mwfr.partner_id = rp.id)" % job_num

        db = SqlService(psycopg2, host, port, user, pwd, database)
        rows = db.ExecQuery(sql)

        jsonStr = '{"list":['
        if len(rows) > 0:
            i = 0
            for row in rows:
                if i == 0:
                    jsonStr += '{"job_num":"'+str(row[0])+'","description":"'+str(row[1])+'","operate_time":"'\
                               + str(self.UTF_time(row[2]))+'","operator":"'+str(row[3])+'","deptment":"'\
                               + str(row[4])+'","matter":"'+str(row[5])+'","state":"'+str(row[6])+'"}'
                    i += 1
                else:
                    jsonStr += ',{"job_num":"'+str(row[0])+'","description":"'+str(row[1])+'","operate_time":"'\
                               + str(self.UTF_time(row[2]))+'","operator":"'+str(row[3])+'","deptment":"'\
                               + str(row[4])+'","matter":"'+str(row[5])+'","state":"'+str(row[6])+'"}'
        jsonStr += '],"info":'

        sql_info = "SELECT soe.r_sph,soe.l_sph,soe.r_cyl,soe.l_cyl,soe.r_axis,soe.l_axis,soe.r_add,soe.l_add," \
                   "soe.r_prism1,soe.l_prism1,soe.r_base1,soe.l_base1,soe.r_prism2,soe.l_prism2,soe.r_base2," \
                   "soe.l_base2,soe.r_ct,soe.l_ct,soe.r_et,soe.l_et,soe.r_base_curve,soe.l_base_curve,soe.r_pd,soe.l_pd," \
                   "soe.r_fh,soe.l_fh,soe.dbl,soe.remark,lo.name l_name,ro.name r_name,soe.l_dia,soe.r_dia,lot.name l_tint,rot.name r_tini " \
                   "FROM (SELECT * from sos_order_export WHERE job_num= '%s') soe " \
                   "LEFT JOIN (SELECT order_id,name from sale_order_line WHERE frl = 'left') lo on lo.order_id = soe.sale_order " \
                   "LEFT JOIN (SELECT order_id,name from sale_order_line WHERE frl = 'right') ro on ro.order_id = soe.sale_order " \
                   "LEFT JOIN (SELECT order_id,name from sale_order_line WHERE frl = 'left_tint') lot on lot.order_id = soe.sale_order " \
                   "LEFT JOIN (SELECT order_id,name from sale_order_line WHERE frl = 'right_tint') rot on rot.order_id = soe.sale_order " % job_num

        rows_info = db.ExecQuery(sql_info)
        if len(rows_info) > 0:
            jsonStr += json.dumps(rows_info[0])
        else:
            jsonStr += "[]"
        jsonStr += "}"
        db.CloseDB()
        return jsonStr.encode()


resource = order_list_resource()
