import os,sys,time
import subprocess
import random
import re
import requests
import urllib3
from get_code import get_authorization_url
from get_key import post_request

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def calculate_g_tk(skey):
    n = 5381
    for c in skey:
        n += (n << 5) + ord(c)
    return n & 2147483647

def showImage(img_path):
    try:
        if sys.platform.find('darwin') >= 0: subprocess.call(['open', img_path])
        elif sys.platform.find('linux') >= 0: subprocess.call(['xdg-open', img_path])
        else: os.startfile(img_path)
    except:
        from PIL import Image
        img = Image.open(img_path)
        img.show()
        img.close()

def removeImage(img_path):
    if sys.platform.find('darwin') >= 0:
        os.system("osascript -e 'quit app \"Preview\"'")
    os.remove(img_path)

def saveImage(img, img_path):
    if os.path.isfile(img_path):
        os.remove(img_path)
    fp = open(img_path, 'wb')
    fp.write(img)
    fp.close()

class qqmusicScanqr():
    is_callable = True
    def __init__(self, **kwargs):
        for key, value in kwargs.items(): setattr(self, key, value)
        self.info = 'login in qqmusic in scanqr mode'
        self.cur_path = os.getcwd()
        self.session = requests.Session()
        self.__initialize()
    '''登录函数'''
    def login(self, username='', password='', crack_captcha_func=None, **kwargs):
        # 设置代理
        self.session.proxies.update(kwargs.get('proxies', {}))
        # 获得pt_login_sig
        params = {
            'appid': '716027609',
            'daid': '383',
            'style': '33',
            'login_text': '授权并登录',
            'hide_title_bar': '1',
            'hide_border': '1',
            'target': 'self',
            's_url': 'https://graph.qq.com/oauth2.0/login_jump',
            'pt_3rd_aid': '100497308',
            'pt_feedback_link': 'https://support.qq.com/products/77942?customInfo=.appid100497308',
        }
        response = self.session.get(self.xlogin_url, params=params)
        pt_login_sig = self.session.cookies.get('pt_login_sig')
        # 获取二维码
        params = {
            'appid': '716027609',
            'e': '2',
            'l': 'M',
            's': '3',
            'd': '72',
            'v': '4',
            't': str(random.random()),
            'daid': '383',
            'pt_3rd_aid': '100497308',
        }
        response = self.session.get(self.ptqrshow_url, params=params)
        saveImage(response.content, os.path.join(self.cur_path, 'qrcode.jpg'))
        showImage(os.path.join(self.cur_path, 'qrcode.jpg'))
        qrsig = self.session.cookies.get('qrsig')
        ptqrtoken = self.__decryptQrsig(qrsig)
        # 检测二维码状态
        while True:
            params = {
                'u1': 'https://graph.qq.com/oauth2.0/login_jump',
                'ptqrtoken': ptqrtoken,
                'ptredirect': '0',
                'h': '1',
                't': '1',
                'g': '1',
                'from_ui': '1',
                'ptlang': '2052',
                'action': '0-0-%s' % int(time.time() * 1000),
                'js_ver': '20102616',
                'js_type': '1',
                'login_sig': pt_login_sig,
                'pt_uistyle': '40',
                'aid': '716027609',
                'daid': '383',
                'pt_3rd_aid': '100497308',
                'has_onekey': '1',
            }
            response = self.session.get(self.ptqrlogin_url, params=params)
            print(response.text)
            if '二维码未失效' in response.text or 'дЇМзїіз†БиЃ§иѓБдЄ≠гАВ' in response.text:pass
            elif '二维码已经失效' in response.text:
                raise RuntimeError('Fail to login, qrcode has expired')
            else:break
            time.sleep(5)
        removeImage(os.path.join(self.cur_path, 'qrcode.jpg'))
        # 登录成功
        qq_number = re.findall(r'&uin=(.+?)&service', response.text)[0]
        url_refresh = re.findall(r"'(https:.*?)'", response.text)[0]
        response1 = self.session.get(url_refresh, allow_redirects=False, verify=False)
        print('账号「%s」登陆成功' % qq_number)
        return self.session

    '''qrsig转ptqrtoken, hash33函数'''
    def __decryptQrsig(self, qrsig):
        e = 0
        for c in qrsig:
            e += (e << 5) + ord(c)
        return 2147483647 & e

    '''初始化'''
    def __initialize(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        }
        self.ptqrshow_url = 'https://ssl.ptlogin2.qq.com/ptqrshow?'
        self.xlogin_url = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?'
        self.ptqrlogin_url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?'
        self.session.headers.update(self.headers)
qq_login = qqmusicScanqr()
session = qq_login.login()
print("session2:",session.cookies)

cookies = session.cookies

# 定义要提取的参数名称
params = ['p_skey', 'pt4_token', 'pt_oauth_token', 'p_uin']
extracted_params = {}

# 遍历 cookies 提取所需参数
for cookie in cookies:
    if cookie.name in params:
        extracted_params[cookie.name] = cookie.value

# 输出提取的参数
for param, value in extracted_params.items():
    print(f"{param}: {value}")

p_skey = extracted_params.get('p_skey')
pt4_token = extracted_params.get('pt4_token')
pt_oauth_token = extracted_params.get('pt_oauth_token')
p_uin = extracted_params.get('p_uin')

g_tk = calculate_g_tk(p_skey)

code = get_authorization_url(p_skey, pt4_token, pt_oauth_token, p_uin, g_tk)

m_key = post_request(g_tk,code)

print(m_key)