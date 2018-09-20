# -*- coding: utf-8 -*-
# @Time    : 2018/9/6 10:10
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : route_proxy_client
# @Software: PyCharm

import evdev
import util
import socket
import time


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ("192.168.1.139", 3390)
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

#准备读取对象
drives = []
kbd_input_list = []
function_key = {}
key_recode = {}

# 初始化usb类键盘设备
usb_temps = util.get_kbd_input_list()
for u_t in usb_temps:
    if u_t not in kbd_input_list:
        print("新加入设备：%s" % u_t)
        drives.append(evdev.InputDevice(util.get_kbd_input_dir()+""+u_t))
        kbd_input_list.append(u_t)
print(drives)
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
                            # 向代理服务发送数据包
                            packet = struct.pack("3s60s20s", "kbd".encode("utf-8"),
                                                 dev.path[19:].encode("utf-8"),
                                                 key_str.encode("utf-8"))
                            packet += "\r\n".encode("utf-8")
                            s.send(packet)
                            # 置空键值缓存
                            key_recode[dev.path] = ""
                        else:
                            # 记录键值
                            key_recode[dev.path] += util.get_hid_print_key(function_key[dev.path], result.code)
                            # 重置功能键
                            if function_key[dev.path]:
                                function_key[dev.path] = False
        except OSError as ose:
            print(ose.__repr__())
            del function_key[dev.path]
            del key_recode[dev.path]
            drives.remove(dev)
            # dev.path[len(util.get_kbd_input_dir()):]
            kbd_input_list.remove(dev.path[19:])
            util.remove_file(dev.path)
            print("接口已拔出: " + dev.path)
        except Exception as e:
            print(e.__repr__())
            print("发生错误")

    # 检测新加入的usb类键盘设备
    usb_temps = util.get_kbd_input_list()
    for u_t in usb_temps:
        if u_t not in kbd_input_list:
            print("新加入设备：%s" % u_t)
            drives.append(evdev.InputDevice(util.get_kbd_input_dir()+""+u_t))
            print(drives)
            kbd_input_list.append(u_t)

