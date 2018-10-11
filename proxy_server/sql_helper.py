# -*- coding: utf-8 -*-
# @Time    : 2018/8/21 22:12
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : sql_helper
# @Software: PyCharm

import pymssql


class SqlService:
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

    def ExecForCursor(self, sql):
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


class MsSqlServer:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise (NameError, "没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.pwd, database=self.db,
                                    charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "连接失败")
        else:
            return cur

    def ExecQuery(self, sql):
        try:
            cur = self.__GetConnect()
            cur.execute(sql)
            data = cur.fetchall()
            row = cur.fetchone()
            rows = cur.fetchmany(10)
        except Exception as e:
            self.conn.rollback()
        finally:
            self.conn.close()

        return data

    def ExecNonQuery(self, sql):
        try:
            cur = self.__GetConnect()
            cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
        finally:
            self.conn.close()