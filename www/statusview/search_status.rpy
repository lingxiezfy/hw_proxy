# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:21
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : search_status
# @Software: PyCharm

import psycopg2
from twisted.web.resource import Resource
import json
import datetime
import os
import configparser


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


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

class order_list_resource(Resource):
    def render_GET(self, request):
        self.render_POST(request)


    def UTF_time(self,time_obj):
        eight_hour = datetime.timedelta(hours=8)
        return time_obj+eight_hour


    def render_POST(self, request):

        real_path = os.path.split(os.path.realpath(__file__))[0]
        config = configparser.ConfigParser(delimiters='=')
        config.read(real_path + "/config.conf", encoding="utf-8")

        host = config["Odoo"]['host']
        port = int(config["Odoo"]['port'])
        user = config["Odoo"]['user']
        pwd = config["Odoo"]['pwd']
        database = config["Odoo"]['database']
        try:
            job_num = request.args[b'job_num'][0].decode("utf-8")
        except:
            print("非法访问")
        sql = "SELECT mwfr.job_num,mwfr.description,mwfr.operate_time,rp.name \"operator\",rr.name \"deptment\", mwfr.matter,mwfr.state from (( " \
        "SELECT mwf.*,mw.resource_id,res_users.partner_id from (SELECT job_num,description,operate_time,operator,deptment,matter,state from mrp_work_flow WHERE job_num = '%s') mwf "\
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
                   "soe.l_base2,soe.r_ct,soe.l_ct,soe.r_et,soe.l_et,soe.r_base_curve,soe.l_base_curve,soe.r_pd," \
                   "soe.l_pd,soe.r_fh,soe.l_fh,soe.dbl,soe.remark,lo.name l_name,ro.name r_name,soe.l_dia," \
                   "soe.r_dia,lot.name l_tint,rot.name r_tini, soe.framename,soe.r_lenname,soe.l_lenname " \
                   "FROM ( " \
                   "select f.*,a.framename,a.r_lenname,a.l_lenname from ( " \
                   "select job_num,max(framename) as framename,max(r_lenname) as r_lenname," \
                   "max(l_lenname) as l_lenname " \
                   "from ( "\
                   "select b.name as job_num," \
                   "case when c.frl='frame' THEN e.name end as framename," \
                   "case when c.frl='right' THEN e.name end as r_lenname," \
                   "case when c.frl='left' THEN e.name end as l_lenname " \
                   "from mrp_production a " \
                   "inner join stock_production_lot b on a.restrict_lot_id=b.id " \
                   "inner join stock_move c on a.\"id\"=c.raw_material_production_id " \
                   "inner join product_product d on c.product_id=d.\"id\" " \
                   "inner join product_template e on d.product_tmpl_id=e.\"id\" " \
                   "where b.name='%s') a group by job_num) a " \
                   "inner join sos_order_export f on a.job_num=f.job_num "\
                   ") soe " \
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