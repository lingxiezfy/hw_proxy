# -*- coding: utf-8 -*-
# @Time    : 2018/9/6 10:10
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : route_proxy_client
# @Software: PyCharm

import configparser
import evdev
import util

#加载桥接端口配置
config = configparser.ConfigParser(delimiters=("=",))
config.read(util.get_curr_path()+"/config/route_config.conf")
in_method_s = config.sections()

#准备读取对象
drives = []
for in_method in in_method_s:
    for option in config.options(in_method):
        if in_method == "usb":
            try:
                drives.append(evdev.InputDevice(option))
            except Exception as e:
                print("接口未使用："+option)

print(drives)
import socket

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
address = ("192.168.1.139", 3390)

#select读取
import select
import struct
while True:
    d,w,x = select.select(drives, [], [])
    for dev in d:
        try:
            for result in dev.read():
                if isinstance(result, evdev.InputEvent):
                    print("code:"+str(result.code))
                    if result.type == evdev.ecodes.EV_KEY and result.value == 0x01:
                        print(str(evdev.ecodes.KEY[result.code])[4:])
                        packet = struct.pack("3s100si", "usb".encode("utf-8"), dev.path.encode("utf-8"), result.code)
                        s.sendto(packet, address)
        except Exception as e:
            print(e.__repr__())
            drives.remove(dev)
            print("接口已拔出"+dev.path)