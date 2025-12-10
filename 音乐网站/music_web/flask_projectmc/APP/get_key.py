import requests
import json

def post_request(g_tk, code):
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://y.qq.com',
        'priority': 'u=1, i',
        'referer': 'https://y.qq.com/',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
        # 'cookie': 'pgv_pvid=1837434580; fqm_pvqid=b5a73133-d32e-4995-8520-93878d959d2b; RK=/8u1egpLcR; ptcz=28a0771cea0ee286aa030a575c33249d792c82c9eff72da653d768a68c4e303b; pac_uid=0_MAxDzAX81w52f; _qimei_uuid42=19214091e00100884c587a93297f1119d47eeac0e6; _qimei_fingerprint=d05ede39451f04ae8211e82eb1a11c2e; _qimei_q36=; _qimei_h38=39682c7a4c587a93297f111902000000419214; suid=user_0_MAxDzAX81w52f; ptui_loginuin=2092923647; ts_uid=1844853700; ts_refer=cn.bing.com/; tmeLoginType=2; music_ignore_pskey=202306271436Hn@vBj; psrf_musickey_createtime=1743987097; psrf_access_token_expiresAt=1749171097; euin=ownqowEAoiCP7z**; qqmusic_key=Q_H_L_63k3NaceeEhr_OHQZCDhi2mnCkSk-b392kaI5bwVMZ7oRDMCIJHT23gyv9ij8BKoXsAY1u6XHlcUEzIyw7unrGQ; fqm_sessionid=b40aeb54-1b80-4a16-8354-06bb4661ee26; pgv_info=ssid=s5111836380; ts_last=y.qq.com/n/ryqq/profile/like/song; _qpsvr_localtk=0.49927275992043585; login_type=1',
    }

    data = f'{{"comm":{{"g_tk":{g_tk},"platform":"yqq","ct":24,"cv":0}},"req":{{"module":"QQConnectLogin.LoginServer","method":"QQLogin","param":{{"code":"{code}"}}}}}}'

    response = requests.post('https://u.y.qq.com/cgi-bin/musicu.fcg', headers=headers, data=data)

    try:
        data = response.json()
        mkey = data["req"]["data"]["musickey"]
        return mkey
    except (KeyError, json.JSONDecodeError) as e:
        raise e