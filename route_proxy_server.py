# -*- coding: utf-8 -*-
# @Time    : 2018/9/5 18:05
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : route_proxy_server
# @Software: PyCharm

import socket
import util
import select
import struct
import configparser


class RouteProxyServer(object):
    def __init__(self, conf):
        self.conf = conf
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # self.server.getsockopt(socket.SOL_SOCKET, socket.TCP_KEEPIDLE, 1800)
        self.server.setblocking(False)

        self.address = ("192.168.1.139", 3390)
        try:
            self.server.bind(self.address)
            self.server.listen()
        except Exception as e:
            print("绑定端口失败")
            raise

        self.function_key = {}
        self.key_recode = {}
        self.login_recode = {}
        self.function_recode = {}
        self.client_info = {}
        self.inputs = []
        self.inputs.append(self.server)

    def is_function_key_value(self, key_value):
        if key_value == "001-FCTEST":
            return True
        return False

    def is_login_key_value(self, key_value):
        if key_value == "001-G18206":
            return True
        return False

    def run(self):
        while True:
            readable, writeable, exceptional = select.select(self.inputs, [], [])
            for server in readable:

                if server is self.server:
                    # 新客户端连接
                    connection,addr = server.accept()
                    print("客户端连接：%s" % str(addr))
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    self.client_info[connection] = str(addr)
                else:
                    # 接收客户端数据
                    try:
                        data = ''.encode("utf-8")
                        total_recv_len = 0
                        while total_recv_len < 108:
                            data_temp = server.recv(108-total_recv_len)
                            data += data_temp
                            total_recv_len += len(data_temp)
                    except Exception as e:
                        print("客户端发生错误" + e.__repr__())

                    if data:
                        print(data)
                        try:
                            type, source, keycode = struct.unpack("3s100si", data)
                        except:
                            print("数据解析有误")
                            continue
                        source_path = source.decode("utf-8").rstrip('\0')
                        data_type = type.decode("utf-8").rstrip('\0')

                        # 类键盘设备数据输入
                        if data_type == 'kbd':
                            if keycode == 42 or keycode == 54:  # 按了左右shift键
                                self.function_key[source_path] = True
                            else:
                                try:
                                    temp_val = self.key_recode[source_path]
                                except KeyError:
                                    self.key_recode[source_path] = ""
                                self.key_recode[source_path] += util.get_hid_print_key(self.function_key.get(source_path, False)
                                                                                       , keycode)
                                self.function_key[source_path] = False
                                # 出现回车,提交一次接受的数据
                                if keycode == 28:
                                    key_value = self.key_recode[source_path]
                                    self.key_recode[source_path] = ""
                                    if self.is_login_key_value(key_value.rstrip("\n")):
                                        # 更新或添加登录信息
                                        print("登录")
                                        self.login_recode[source_path] = key_value.rstrip("\n")
                                    elif self.is_function_key_value(key_value.rstrip("\n")):
                                        # 设置当前功能
                                        print("设置功能")
                                        self.function_recode[source_path] = key_value.rstrip("\n")
                                    else:
                                        print("收到键码")
                                        # 登录信息以及功能信息完备才进行相应的业务处理
                                        login_value = self.login_recode.get(source_path, None)
                                        function_value = self.function_recode.get(source_path, None)
                                        msg = ""
                                        if login_value is None:
                                            msg = "未登录"
                                        elif function_value is None:
                                            msg = "未设置功能"
                                        else:
                                            msg = login_value + ":" + function_value + ":" + addr[0] + ":"+str(addr[1]) + ":" + \
                                                  source_path + ":" + str(key_value)
                                        print(msg)
                                        curr_path = util.get_curr_path()
                                        direct = curr_path+"/no_direct.txt"
                                        try:
                                            direct = curr_path+"/"+(self.conf.get(data_type, source_path).replace(":", "_"))
                                        except configparser.NoOptionError:
                                            pass
                                        f = open(direct, "a")
                                        f.write(key_value)
                                        f.close()

                        else:
                            # 其他类型数据
                            pass
                    else:
                        print("客户端断开：%s" % str(self.client_info[server]))
                        self.inputs.remove(server)
                        server.close()
                        del self.client_info[server]

if __name__ == "__main__":
    config = configparser.ConfigParser(delimiters=("=",))
    config.read("config/route_config.conf")
    server = RouteProxyServer(config)
    server.run()

