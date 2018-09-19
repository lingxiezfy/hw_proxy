# -*- coding: utf-8 -*-
# @Time    : 2018/9/6 10:10
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : route_proxy_client
# @Software: PyCharm

import configparser
import evdev
import util
import traceback

#加载桥接端口配置
config = configparser.ConfigParser(delimiters=("=",))
config.read(util.get_curr_path()+"/config/route_config.conf")
in_method_s = config.sections()

#准备读取对象
drives = []
for in_method in in_method_s:
    for option in config.options(in_method):
        if in_method == "kbd":
            try:
                drives.append(evdev.InputDevice(option))
            except Exception as e:
                print("接口未使用："+option)

print(drives)
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ("192.168.1.139", 3390)
import time
i = 0
while True:
    i += 1
    rc = s.connect_ex(address)
    if not rc:
        print("连接成功")
        break
    print("连接服务器失败,第%d次尝试" % i)
    time.sleep(10)



#select读取
import select
import struct

function_key = {}
key_recode = {}
while True:

    d, w, x = select.select(drives, [], [])
    for dev in d:
        try:
            for result in dev.read():
                if isinstance(result, evdev.InputEvent):
                    if result.type == evdev.ecodes.EV_KEY and result.value == 0x01:
                        print(str(evdev.ecodes.KEY[result.code])[4:])
                        # 初始化记录键值缓存
                        if dev.path not in key_recode:
                            key_recode[dev.path] = ""
                        # 初始化功能键缓存
                        if dev.path not in function_key:
                            function_key[dev.path] = False
                        # 分析键值（功能键，回车键，或普通键）
                        if result.code == 42 or result.code == 54:
                            function_key[dev.path] = True
                        elif result.code == 28:
                            key_str = key_recode[dev.path]
                            key_str += "\r\n"
                            packet = struct.pack("3s100si", "kbd".encode("utf-8"), dev.path.encode("utf-8"),
                                                 result.code)
                            s.sendall(packet)
                            s.send(key_str.encode())
                            # 置空键值缓存
                            key_recode[dev.path] = ""
                        else:
                            # 记录键值
                            key_recode[dev.path] += util.get_hid_print_key(function_key[dev.path], result.code)
                            # 重置功能键
                            if function_key[dev.path]:
                                function_key[dev.path] = False

        except Exception as e:
            print(traceback.print_exc())
            print(e.__repr__())
            drives.remove(dev)
            print("接口已拔出"+dev.path)