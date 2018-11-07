# -*- coding: utf-8 -*-
# @Time    : 2018/9/5 15:27
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : util
# @Software: PyCharm

import os
import re

kbd_input_path = "/dev/input/by-path/"


def get_curr_path():
    return os.path.split(os.path.realpath(__file__))[0]


def get_kbd_input_dir():
    return kbd_input_path


def remove_file(path):
    try:
        os.remove(path)
    except:
        pass


def get_kbd_input_list():
    try:
        input_list = os.listdir(kbd_input_path)
    except FileNotFoundError:
        return []
    k_list = []
    for input_item in input_list:
        k_list.append(input_item) if re.match(r"pci-.*?-usb-.*?-event-kbd", input_item, re.I) else None
    return k_list


def _make_file_path(path, filename):
    return path+filename


def get_hid_print_key(has_function_key,usb_kbd_keycode, usb_kbd_key):
    hid_print_usually_key = [None, None, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', None,
                     None, 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n', None,
                     'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', None, '\\',
                     'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', None, '*', None,
                     ' ', None]

    hid_print_shift_key = [None, None, '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', None,
                             None, 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '\n', None,
                             'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', '~', None, '|',
                             'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', None, '*', None,
                             ' ', None]
    hid_print_keypid = {'KEY_KPSLASH':'/','KEY_KPMINUS':'-','KEY_KPDOT':'.','KEY_KPPLUS':'+',
                        'KEY_KPCOMMA':',','KEY_KPEQUAL':'=',
                        'KEY_KP0':'0','KEY_KP1':'1','KEY_KP2':'2','KEY_KP3':'3','KEY_KP4':'4',
                        'KEY_KP5':'5','KEY_KP6':'6','KEY_KP7':'7','KEY_KP8':'8','KEY_KP9':'9',}
    if usb_kbd_keycode <= 58:
        if has_function_key:
            return hid_print_shift_key[usb_kbd_keycode]
        else:
            return hid_print_usually_key[usb_kbd_keycode]
    elif usb_kbd_key in hid_print_keypid:
        return hid_print_keypid[usb_kbd_key]
    else:
        return None

