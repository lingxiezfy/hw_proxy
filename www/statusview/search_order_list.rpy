# -*- coding: utf-8 -*-
# @Time    : 2018/9/13 17:21
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : search_order_list
# @Software: PyCharm

import pymysql
from twisted.web.resource import Resource
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

    def render_POST(self, request):
        host = '192.168.1.240'
        port = 3306
        user = 'lensware'
        pwd = 'lensware'
        database = 'lwr_ginoptic'
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

        CustNumb = request.args[b'CustNumb'][0].decode("utf-8")
        OrdNumbH = request.args[b'OrdNumbH'][0].decode("utf-8")
        Reference = request.args[b'Reference'][0].decode("utf-8")
        Status = request.args[b'Status'][0].decode("utf-8")
        EntryDate = request.args[b'EntryDate'][0].decode("utf-8")

        search_str = ""
        if CustNumb:
            search_str += "AND CustNumb LIKE '%"+CustNumb+"%' "
        if OrdNumbH:
            search_str += "AND OrdNumbH LIKE '%"+OrdNumbH+"%' "
        if Reference:
            search_str += "AND Reference LIKE '%"+Reference+"%' "
        if Status:
            search_str += "AND Status LIKE '%"+Status+"%' "
        if EntryDate:
            ls = EntryDate.split("-")
            the_date = datetime.datetime(int(ls[0]), int(ls[1]), int(ls[2]))
            pre_date = the_date + datetime.timedelta(days=1)
            pre_data_str = pre_date.strftime('%Y-%m-%d')
            search_str += "AND EntryDate >= '"+EntryDate+"' AND EntryDate < '"+pre_data_str+"' "
        sql = "SELECT CustNumb,Rectype,Reference,OrdNumbH,ReqDelv,EntryDate,Status " \
              "FROM order_header where 1=1 "
        sql += search_str
        sql += "ORDER BY EntryDate desc LIMIT %d,%d" % (startNum, pageSize)
        db = SqlService(pymysql, host, port, user, pwd, database)
        rows = db.ExecQuery(sql)
        jsonStr = '{"list":['
        if len(rows) > 0:
            i = 0
            for row in rows:
                if i == 0:
                    jsonStr += '{"CustNumb":"'+row[0]+'","Rectype":"'+row[1]+'","Reference":"'+row[2]+'","OrdNumbH":"'+row[3]+'","ReqDelv":"'+str(row[4])+'","EntryDate":"'+str(row[5])+'","Status":"'+row[6]+'"}'
                    i += 1
                else:
                    jsonStr += ',{"CustNumb":"' + row[0] + '","Rectype":"' + row[1] + '","Reference":"' + row[
                        2] + '","OrdNumbH":"' + row[3] + '","ReqDelv":"' + str(row[4]) + '","EntryDate":"' + str(row[5]) + '","Status":"' + row[6] + '"}'

            sql_count = "SELECT count(*) from order_header where 1=1 "
            sql_count += search_str
            row_count = db.ExecQuery(sql_count)
            totalRow = int(row_count[0][0])
        db.CloseDB()
        jsonStr += '],"totalRow":'+str(totalRow)+',"pageNumber":'+str(pageNumber)+',"pageSize":'+str(pageSize)+'}'

        return jsonStr.encode()

resource = order_list_resource()