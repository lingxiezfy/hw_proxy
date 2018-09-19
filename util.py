# -*- coding: utf-8 -*-
# @Time    : 2018/9/5 15:27
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : util
# @Software: PyCharm

import os

kbd_input_path = "/dev/input/by-path/"


def get_curr_path():
    return os.path.split(os.path.realpath(__file__))[0]


def get_kbd_input_dir():
    return kbd_input_path


def remove_file(path):
    try:
        os.remove(path)
    except Exception as e:
        pass

def get_kbd_input_list():
    try:
        return os.listdir(kbd_input_path)
    except FileNotFoundError:
        return []


def _make_file_path(path, filename):
    return path+filename


def get_hid_print_key(has_function_key,usb_kbd_keycode):
    hid_print_usually_key = [None, None, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', None,
                     None, 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n', None,
                     'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', None, '\\',
                     'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', None, None, None,
                     ' ', None]

    hid_print_shift_key = [None, None, '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', None,
                             None, 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '\n', None,
                             'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', '~', None, '|',
                             'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', None, None, None,
                             ' ', None]
    if has_function_key:
        return hid_print_shift_key[usb_kbd_keycode]
    else:
        return hid_print_usually_key[usb_kbd_keycode]
