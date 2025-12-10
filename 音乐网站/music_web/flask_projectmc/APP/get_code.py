import requests
import time

def get_authorization_url(p_skey, pt4_token, pt_oauth_token, p_uin ,g_tk):
    cookies = {
        'tmeLoginType': '2',
        '_qpsvr_localtk': '0.09456172802034679',
        'p_uin': p_uin ,
        'pt_login_type': '3',
        'pt4_token': pt4_token,
        'p_skey': p_skey,
        'pt_oauth_token': pt_oauth_token,
    }

    data = {
        'response_type': 'code',
        'client_id': '100497308',
        'redirect_uri': 'https://y.qq.com/portal/wx_redirect.html?login_type=1&surl=https%3A%2F%2Fy.qq.com%2F',
        'scope': 'get_user_info,get_app_friends',
        'state': 'state',
        'switch': '',
        'from_ptlogin': '1',
        'src': '1',
        'update_auth': '1',
        'openapi': '1010_1030',
        'g_tk': g_tk,
        'auth_time': str(int(time.time())*1000),
    }

    response = requests.post('https://graph.qq.com/oauth2.0/authorize', cookies=cookies, data=data)

    url = response.url

    query_start = url.find('?')
    if query_start != -1:
        query_string = url[query_start + 1:]
        # 分割每个参数
        params = query_string.split('&')
        for param in params:
            if param.startswith('code='):
                code = param[len('code='):]
                return code
        else:
            return None
    else:
        return None
