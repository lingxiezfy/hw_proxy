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
        self.server.setblocking(False)
        self.function_key = {}
        self.key_value = {}
        try:
            self.address = ("192.168.1.139", 3390)
            self.server.bind(self.address)
        except Exception as e:
            print("绑定端口失败")
            raise

    def run(self):
        while True:
            s,w,e = select.select([self.server,],[],[])
            for server in s:
                data, addr = server.recvfrom(2048)

                type,source,keycode = struct.unpack("3s100si", data)
                source_path = source.decode("utf-8").rstrip('\0')
                data_type = type.decode("utf-8").rstrip('\0')

                if data_type == 'usb':
                    if keycode == 42 or keycode == 54:  #按了左右shift键
                        self.function_key[source_path] = True
                    else:
                        try:
                            key_temp_val = self.key_value[source_path]
                        except KeyError:
                            self.key_value[source_path] = ""
                        self.key_value[source_path] += util.get_hid_print_key(self.function_key.get(source_path, False),
                                                                              keycode)
                        self.function_key[source_path] = False
                        if keycode == 28: #出现回车
                            key_value = self.key_value[source_path]
                            self.key_value[source_path] = ""
                            print(key_value)
                            curr_path = util.get_curr_path()
                            drict = curr_path+"/no_dirct.txt"
                            try:
                                drict = curr_path+"/"+(self.conf.get(data_type, source_path).replace(":", "_"))
                            except configparser.NoOptionError:
                                pass

                            f = open(drict, "a")
                            f.write(key_value)
                            f.close()


                else:
                    pass






if __name__ == "__main__":
    config = configparser.ConfigParser(delimiters=("=",))
    config.read("config/route_config.conf")
    server = RouteProxyServer(config)
    server.run()

