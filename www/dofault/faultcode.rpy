# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 17:24
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : faultcode
# @Software: PyCharm

from twisted.web.resource import Resource
import csv
import os
import json
import traceback

def get_fault_info_from_csv(_path):
    fault_list = []
    section_list = []
    with open(_path, encoding='UTF-8-sig', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        _temp = ''
        for row in reader:
            s_c = row['section_code']
            if s_c not in _temp:
                _temp += s_c
                section_list.append({'section_code': s_c,
                                     'section_name': row['section']})
            fault_list.append({'section_code': s_c,
                               'fault_code': row['faultcode'],
                               'fault_name': row['faultname'],
                               'frl': row['frl']})
    fault_dir = {
        'code': 1,
        'section_list': section_list,
        'fault_list': fault_list
    }
    return fault_dir


class FalutCode(Resource):

    def render_GET(self, request):
        return self.render_POST(request)

    def render_POST(self, request):
        try:
            real_path = os.path.split(os.path.realpath(__file__))[0]
            break_type = request.args[b'break_type'][0].decode("utf-8")
            if break_type == 'B':
                fault_info = get_fault_info_from_csv(real_path + '/BadFault.csv')
            elif break_type == 'S':
                fault_info = get_fault_info_from_csv(real_path + '/ScrapFault.csv')
            else:
                raise TypeError("无效错误代码")
            json_str = json.dumps(fault_info)
        except:
            print(traceback.print_exc())
            json_str = '{"code":0}'
        return json_str.encode('utf-8')


resource = FalutCode()
