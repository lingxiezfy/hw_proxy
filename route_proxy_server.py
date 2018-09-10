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
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(False)
        self.function_key = {}
        self.key_recode = {}
        self.login_recode = {}
        self.function_recode = {}
        self.address = ("192.168.1.139", 3390)
        try:
            self.server.bind(self.address)
        except Exception as e:
            print("绑定端口失败")
            raise

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
            readable, writeable, exceptional = select.select([self.server, ], [], [])
            for server in readable:
                data, addr = server.recvfrom(512)

                type, source, keycode = struct.unpack("3s100si", data)
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


if __name__ == "__main__":
    config = configparser.ConfigParser(delimiters=("=",))
    config.read("config/route_config.conf")
    server = RouteProxyServer(config)
    server.run()

