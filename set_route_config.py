# -*- coding: utf-8 -*-
# @Time    : 2018/9/5 15:25
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : set_bridge_config
# @Software: PyCharm

import configparser
import util


def print_config(conf):
    for section in conf.sections():
        print(section+":")
        for item in conf.items(section):
            print(item)


def set_usb_config(conf, input_s):
    if "kbd" not in conf.sections():
        conf.add_section("kbd")
    for input_file in input_s:
        conf.set("kbd", util.get_usb_input_dir()+input_file, input_file+".txt")
    f = open(util.get_curr_path()+"/config/route_config.conf", "w")
    conf.write(f)
    f.close()


config = configparser.ConfigParser(delimiters=("=",))
config.read(util.get_curr_path()+"/config/route_config.conf")
print_config(config)
usb_input_s = util.get_usb_input_list()
print(usb_input_s)
set_usb_config(config, usb_input_s)
print_config(config)


