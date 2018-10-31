# -*- coding: utf-8 -*-
# @Time    : 2018/9/6 10:10
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : route_proxy_client
# @Software: PyCharm

import evdev
import scan_util
import socket
import time
import configparser
import os
import logging
from logging.handlers import TimedRotatingFileHandler

config = configparser.ConfigParser(delimiters='=')
config.read(os.path.split(os.path.realpath(__file__))[0] + "/config.conf", encoding="utf-8")

logger = logging.getLogger('Scan')
logger.setLevel(logging.DEBUG)

real_path = os.path.split(os.path.realpath(__file__))[0]
fn = real_path + '/log/log.log'

fh = TimedRotatingFileHandler(fn, when='D', interval=1, backupCount=10, encoding='utf-8')
# fh = logging.FileHandler(fn, encoding='utf-8')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

proxy_host = config["proxyServer"]["proxy_host"]
proxy_port = int(config["proxyServer"]["proxy_port"])
max_data_length = int(config["scanClient"]["max_data_length"])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_is_connected = False


def connect_proxy_loop():
    address = (proxy_host, proxy_port)
    i = 0
    while True:
        i += 1
        rc = s.connect_ex(address)
        if not rc:
            logger.info("连接代理服务器 host:%s - port:%s 成功 %s " % (proxy_host, proxy_port, s))
            return True
        logger.info("连接代理服务器 host:%s - port:%s 失败,第%d次尝试" % (proxy_host, proxy_port, i))
        time.sleep(10)


proxy_is_connected = connect_proxy_loop()

import select
import struct

# 准备读取对象
drives = []
kbd_input_list = []
function_key = {}
key_recode = {}


# 扫描usb类键盘设备
def get_drivers():
    usb_temps = scan_util.get_kbd_input_list()
    for u_t in usb_temps:
        if u_t not in kbd_input_list:
            logger.info("发现设备：%s" % u_t)
            drives.append(evdev.InputDevice(scan_util.get_kbd_input_dir()+""+u_t))
            kbd_input_list.append(u_t)


get_drivers()

logger.info("程序开始监听")
while True:

    d, w, x = select.select(drives, [], [], 2)
    if proxy_is_connected:
        for dev in d:
            try:
                for result in dev.read():
                    if isinstance(result, evdev.InputEvent):
                        if result.type == evdev.ecodes.EV_KEY and result.value == 0x01:
                            # print(str(evdev.ecodes.KEY[result.code])[4:])
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
                                # 置空键值缓存
                                key_recode[dev.path] = ""
                                try:
                                    s.send(packet)
                                    logger.info("发送数据 - %s - %s" % (dev.path[19:], key_str))
                                except Exception as e:
                                    logger.error("丢失代理服务器 %s " % s)
                                    proxy_is_connected = False

                            else:
                                # 记录键值
                                key_recode[dev.path] += scan_util.get_hid_print_key(function_key[dev.path], result.code)
                                # 清除脏数据
                                if len(key_recode[dev.path]) == max_data_length:
                                    logger.info("清除数据 - %s - %s" % (dev.path[19:], key_recode[dev.path]))
                                    key_recode[dev.path] = ""
                                # 重置功能键
                                if function_key[dev.path]:
                                    function_key[dev.path] = False
            except OSError as ose:
                try:
                    del function_key[dev.path]
                    del key_recode[dev.path]
                except KeyError as ke:
                    pass
                drives.remove(dev)
                # dev.path[len(util.get_kbd_input_dir()):]
                kbd_input_list.remove(dev.path[19:])
                scan_util.remove_file(dev.path)
                logger.info("输入设备已拔出 - %s " % dev.path)
            except Exception as e:
                logger.error("发生错误-请重启后再试- %s " % e.__repr__())

        # 检测新加入的usb类键盘设备
        get_drivers()
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_is_connected = connect_proxy_loop()




