# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:21
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : search_picking_list
# @Software: PyCharm

import psycopg2
from twisted.web.resource import Resource
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


class order_list_resource(Resource):
    def render_GET(self, request):
        return self.render_POST(request)

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
            pageSize = int(request.args[b'pageSize'][0].decode("utf-8"))
            pageNumber = int(request.args[b'pageNumber'][0].decode("utf-8"))
        except:
            pageNumber = 1
            pageSize = 10
        if pageNumber <= 0:
            pageNumber = 1
        startNum = pageSize * (pageNumber - 1)
        totalRow = 0

        job_num = request.args[b'job_num'][0].decode("utf-8")
        operator_login = request.args[b'operator_login'][0].decode("utf-8")
        picking_type = request.args[b'picking_type'][0].decode("utf-8")
        picking_time_start = request.args[b'picking_time_start'][0].decode("utf-8")
        picking_time_end = request.args[b'picking_time_end'][0].decode("utf-8")
        db = SqlService(psycopg2, host, port, user, pwd, database)
        search_str = ""
        if operator_login:
            sql = "SELECT id from res_users WHERE \"login\" = '"
            if len(operator_login) > 6 and operator_login.startswith('9999'):
                sql += operator_login[4:]
            else:
                sql += operator_login
            sql += "'"
            rows = db.ExecQuery(sql)
            if len(rows) > 0:
                uid = rows[0][0]
                search_str += "AND uid = '"+str(uid)+"' "
        if job_num:
            search_str += "AND job_num LIKE '%"+job_num+"%' "

        if picking_type:
            search_str += "AND picking_type LIKE '%"+picking_type+"%' "
        if picking_time_start:
            search_str += "AND picking_time >= '"+picking_time_start + "' "
        if picking_time_end:
            search_str += "AND picking_time < '" + picking_time_end + "' "
        sql = "select job_num,picking_time,picking_type,name operator_name from ("
        sql += "SELECT * from picking_history WHERE 1=1 "
        sql += search_str
        sql += " ORDER BY id desc LIMIT %d OFFSET %d" % (pageSize, startNum)
        sql += ") ph " \
               "LEFT JOIN (SELECT ru.id ru_id,ru.partner_id from res_users ru) ru on ph.uid = ru.ru_id " \
               "LEFT JOIN (SELECT rp.id rp_id,rp.name FROM res_partner rp) rp on ru.partner_id = rp.rp_id"

        rows = db.ExecQuery(sql)
        jsonStr = '{"list":['
        if len(rows) > 0:
            i = 0
            for row in rows:
                if i == 0:
                    jsonStr += '{"job_num":"'+row[0]+'","picking_time":"'+str(row[1]) + \
                               '","picking_type":"'+row[2]+'","operator_name":"'+row[3]+'"}'
                    i += 1
                else:
                    jsonStr += ',{"job_num":"'+row[0]+'","picking_time":"'+str(row[1]) + \
                               '","picking_type":"'+row[2]+'","operator_name":"'+row[3]+'"}'
            sql_count = "SELECT count(*) from picking_history WHERE 1=1 "
            sql_count += search_str
            row_count = db.ExecQuery(sql_count)
            totalRow = int(row_count[0][0])
        db.CloseDB()
        jsonStr += '],"totalRow":'+str(totalRow)+',"pageNumber":'+str(pageNumber)+',"pageSize":'+str(pageSize)+'}'
        return jsonStr.encode()

resource = order_list_resource()

