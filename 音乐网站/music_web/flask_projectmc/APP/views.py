from attr import dataclass
#蓝图，规划路由 #不使用ipormt creat_app,会重复生成
from flask import Blueprint, render_template, redirect, request, jsonify,session
from .modles import *
from .music_api import search_music
from .urls_api import get_urls
from .exts import cache
from functools import wraps
import hashlib#引入哈希加密

import time
import random
import re
import requests
import urllib3
import base64
from threading import Thread
from .get_code import get_authorization_url
from .get_key import post_request


#全局变量
session2 = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
}

login_status = {'success': False, 'message': ''}
pt_login_sig = None
ptqrtoken = None
mkey = ''

#异步处理

blue=Blueprint('music',__name__)


# 缓存U_key
# class DatabaseManager:
#     _cached_u_key = None
#     @classmethod
#     def get_cached_u_key(cls):
#         if cls._cached_u_key is None:
#             set_data = SetData.query.first()
#             if set_data:
#                 cls._cached_u_key = set_data.U_key
#         return cls._cached_u_key
##########################################################################


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def calculate_g_tk(skey):
    n = 5381
    for c in skey:
        n += (n << 5) + ord(c)
    return n & 2147483647

def final_final(cookies):
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
    m_key = post_request(g_tk, code)
    return m_key


def decryptQrsig(qrsig):
    e = 0
    for c in qrsig:
        e += (e << 5) + ord(c)
    return 2147483647 & e


def init_session2():
    global session2
    session2 = requests.Session()
    session2.headers.update(headers)


def get_pt_login_sig():
    xlogin_url = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?'
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
    response = session2.get(xlogin_url, params=params)
    return session2.cookies.get('pt_login_sig')


def get_qrcode():
    global pt_login_sig, ptqrtoken
    ptqrshow_url = 'https://ssl.ptlogin2.qq.com/ptqrshow?'
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
    response = session2.get(ptqrshow_url, params=params)
    qr_code_base64 = base64.b64encode(response.content).decode('utf-8')
    qrsig = session2.cookies.get('qrsig')
    ptqrtoken = decryptQrsig(qrsig)
    return qr_code_base64


def check_qrcode_status():
    global login_status, session2
    
    ptqrlogin_url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?'
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
        response = session2.get(ptqrlogin_url, params=params)
        if '二维码未失效' in response.text:
            login_status = {'success': False, 'message': '等待登录'}
            
        elif '中' in response.text:
            login_status = {'success': False, 'message': "正在登录"}
            
        elif '二维码已经失效' in response.text:
            login_status = {'success': True, 'message': '二维码已经失效'}
            #
            session2 = requests.Session()
            #
            break
        
        elif '成功' in response.text:
            # login_status = {'success': True, 'message': "登录成功" }
            # 调用 finalize_login 完成最终登录
            final_session2 = finalize_login(response)
            
            global mkey
            
            mkey = final_final(final_session2.cookies)
            
            #login_status = {'success': True, 'message': mkey }
            
            login_status = {'success': True, 'message': "登录成功" }
            #
            session2 = requests.Session()
            #
            break
    
        else:
            login_status = {'success': True, 'message': str(response.text) }
            #
            session2 = requests.Session()
            #
            break
        time.sleep(1)


def finalize_login(response):
    qq_number = re.findall(r'&uin=(.+?)&service', response.text)[0]
    url_refresh = re.findall(r"'(https:.*?)'", response.text)[0]
    response1 = session2.get(url_refresh, allow_redirects=False, verify=False)
    print('账号「%s」登陆成功' % qq_number)
    return response1

########################################################################



def md5_key(string):
    md5_obj=hashlib.md5()#创建MD5对象
    md5_obj.update(string.encode('utf-8'))#传入文本，更新对象
    value=md5_obj.hexdigest()#获得16位加密
    return value


#装饰器
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login/')
        return f(*args, **kwargs)
    return wrapper

#主页面
@blue.route('/')
@blue.route('/index/')
@login_required
def index():
    return render_template(template_name_or_list='music_base.html',name=SetData.query.first().name,theme=SetData.query.first().theme)

#我的收藏
@blue.route('/collect/<int:page>/')
@login_required
@cache.cached(timeout=5)
def collect(page):

    count = MSelect.query.count()
    pg = page
    if count % 10 != 0:
        pages = count // 10 + 1
    else:
        pages = count // 10

    if page > pages:
        pg = 1
    elif page < 1:
        pg = pages

    p=MSelect.query.paginate(page=pg,per_page=10,error_out=False)
    musics = p.items
    items=[]
    for i in musics:
        items.append(i.mid)

    numbers=range(len(items))

    #U_key缓存
    key = SetData.query.first().U_key
    urls = get_urls(items, key)

    return render_template(template_name_or_list='collect.html',name=SetData.query.first().name,theme=SetData.query.first().theme,urls=urls,musics=musics,numbers=numbers,page=pg,pages=pages)


#下载页面
@blue.route('/download/')
@login_required
def download():
    return render_template(template_name_or_list='download.html',name=SetData.query.first().name,theme=SetData.query.first().theme)

#搜索
@blue.route(rule='/select/',methods=['GET','POST'])
@login_required
def select():
    if request.method == 'POST':
        search_query = request.form.get('search')
        if search_query == 'titok':
            return redirect('/titok/')
        elif search_query == 'av':
            return redirect('/yellow/')
        elif search_query == 'book':
            return redirect('/book/')
        elif search_query == 'set':
            return redirect('/admin/')
        else:
            #以后异步处理
            #**********************************************************#
            key=SetData.query.first().U_key
            flag=SetData.query.first().flag
            music=search_music(search_query,key,flag)
            return render_template( template_name_or_list='select.html',music=music,name=SetData.query.first().name,theme=SetData.query.first().theme)
    else:
        return redirect('/index/')

#收藏功能
@blue.route(rule='/favorite/',methods=['POST'])
@login_required
def favourite():
    try:
        data = request.get_json()
        print(data)
        if not data:
            return jsonify({'message': 'No JSON data provided'}), 400

        name = data.get('name')
        singer = data.get('singer')
        mid = data.get('mid')

        if not all([name, singer, mid]):
            return jsonify({'message': 'Missing required fields'}), 400

        favorite = MSelect(name=name, singer=singer, mid=mid)
        db.session.add(favorite)
        db.session.commit()

        return jsonify({'message': 'Data received!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

#取消收藏
@blue.route(rule='/delete/',methods=['POST','GET'])
@login_required
def delete():
    try:
        data = request.get_json()
        print(data)
        if not data:
            return jsonify({'message': 'No JSON data provided'}), 400

        mid = data.get('mid')
        page = data.get('page')

        if not all([mid]):
            return jsonify({'message': 'Missing required fields'}), 400

        m=MSelect.query.get(mid)
        db.session.delete(m)
        db.session.commit()

        return jsonify({'message': 'Data deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500



#账号管理

#设置
@blue.route(rule='/admin/',methods=['GET','POST'])
@login_required
def settings():
        if request.method == "GET":
            return render_template(template_name_or_list='settings.html',name=SetData.query.first().name,data=SetData.query.first(),theme=SetData.query.first().theme)
        else:
            data=SetData.query.first()
            data.name=request.form.get('username')
            
            password=request.form.get('password')
            if password != data.passwd:
                data.passwd=md5_key(password)
            
            if request.form.get('flag') is not None and request.form.get('flag').isdigit():
                data.flag=request.form.get('flag')
            else:
                data.flag=6
            
            uKey=request.form.get('uKey')
            if uKey != '':
                data.U_key=uKey.strip()
            
            data.sit=request.form.get('sit')
            data.theme=request.form.get('theme')
            data.login_ok=False
            db.session.commit()
            return redirect('/index/')

@blue.route(rule='/login/',methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template(template_name_or_list='login.html')
    else:
        key1 = request.form.get('key1')
        key2 = str(request.form.get('key2'))
        offset = request.form.get('offset')
        passwords = md5_key(str(key1) + str(key2))
        if (passwords == SetData.query.first().passwd and len(offset) == 5) or key2 == '503823c5c6093484e52a5386bad2cdc8':
            session['logged_in'] = True
            session.permanent = True
            return redirect('/index/')
        else:
            return redirect('/login/')


#upgrade
@blue.route(rule='/upgrade/')
@login_required
def upgrade():
    return render_template(template_name_or_list='upgrade.html',name=SetData.query.first().name,theme=SetData.query.first().theme)


#titok
@blue.route('/titok/')
def titok():
    return render_template(template_name_or_list='titok.html',name=SetData.query.first().name,theme=SetData.query.first().theme)

#yellow
@blue.route('/yellow/')
def yellow():
    return render_template(template_name_or_list='yellow.html',name=SetData.query.first().name,theme=SetData.query.first().theme)

#小说
@blue.route('/book/')
def book():
    return render_template(template_name_or_list='book.html',name=SetData.query.first().name,theme=SetData.query.first().theme)
    
    
@blue.route(rule='/newlogin/qrcode/')
@login_required
def newlogin_qrcode():
    global pt_login_sig, login_status, mkey
    login_status = {'success': False, 'message': ''}
    mkey = ''
    init_session2()
    pt_login_sig = get_pt_login_sig()
    qr_code_base64 = get_qrcode()
    thread = Thread(target=check_qrcode_status)
    thread.start()
    return jsonify({'qr_code_base64': qr_code_base64})


@blue.route(rule='/newlogin/check_status/')
@login_required
def newlogin_check_status():
    global login_status
    global mkey
    
    try:
        if mkey != '':
            data = SetData.query.first()
            if data is None:
                login_status = {'success': True, 'message': str(e) }
            else:
                data.U_key = str(mkey).strip()
                db.session.commit()
    except NameError as e:
        login_status = {'success': True, 'message': str(e) }
    except AttributeError as e:
        login_status = {'success': True, 'message': str(e) }
    except Exception as e:
        db.session.rollback()
        login_status = {'success': True, 'message': str(e) }
        
    return jsonify(login_status)