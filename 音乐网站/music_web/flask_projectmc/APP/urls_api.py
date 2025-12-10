import requests
from jsonpath import jsonpath
def get_urls(items,key):
    cookie = {
        'pgv_pvid': '1837434580',
        'fqm_pvqid': 'b5a73133-d32e-4995-8520-93878d959d2b',
        'RK': '/8u1egpLcR',
        'ptcz': '28a0771cea0ee286aa030a575c33249d792c82c9eff72da653d768a68c4e303b',
        'pac_uid': '0_MAxDzAX81w52f',
        '_qimei_uuid42': '19214091e00100884c587a93297f1119d47eeac0e6',
        '_qimei_fingerprint': 'd05ede39451f04ae8211e82eb1a11c2e',
        '_qimei_q36': '',
        '_qimei_h38': '39682c7a4c587a93297f111902000000419214',
        'suid': 'user_0_MAxDzAX81w52f',
        'ptui_loginuin': '2092923647',
        'ts_uid': '1844853700',
        'ts_refer': 'cn.bing.com/',
        'tmeLoginType': '2',
        'music_ignore_pskey': '202306271436Hn@vBj',
        '_tucao_custom_info': 'N0xxbTZWT0gxTHN6bEJ3bUMvT25rSFRxQXMydk8xSUhxUG5HV0MwZFZWd0RVUzF0bTk3dXVpdHpTZzRnb0FsTg%3D%3D--tbGT7eZeyEMYpDFNThaoDw%3D%3D--ZTkyZGRjNzM4M2EyZDAzMDhhMDFiMjcwOWUyN2ZhOGM%3D',
        'fqm_sessionid': 'c9587a38-e449-45fb-a7b9-d4d2f0cc4bd2',
        'pgv_info': 'ssid=s6647489086',
        '_qpsvr_localtk': '0.6526246706640442',
        'login_type': '1',
        'qqmusic_key': f'{key}',
        'euin': 'ownqowEAoiCP7z**',
        'psrf_access_token_expiresAt': '1749207113',
        'wxunionid': '',
        'psrf_qqopenid': '00F03BBF2711E6E57F3022113C288745',
        'uin': '2092923647',
        'qm_keyst': f'{key}',
        'wxrefresh_token': '',
        'psrf_qqaccess_token': 'D185278E317E55DB5B4824C853260B5C',
        'wxopenid': '',
        'psrf_qqunionid': 'BF80135E48237BC20A08D84F2AAD00CE',
        'psrf_qqrefresh_token': 'B0FD9834461D49F04FAC26166DAB0387',
        'psrf_musickey_createtime': '1744023113',
        'ts_last': 'y.qq.com/n/ryqq/search',
    }
    

    head_search = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
    }

    urls = []
    for i in items:

        music_data_url = rf'https://u.y.qq.com/cgi-bin/musicu.fcg?data={{"comm":{{"cv":4747474,"ct":24,"format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"yqq.json","needNewCode":1,"uin":"1152921504916411742","g_tk_new_20200303":1849600344,"g_tk":1849600344}},"req_9":{{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{{"guid":"4868259520","songmid":["{ i }"],"songtype":[0],"uin":"1152921504916411742","loginflag":1,"platform":"20"}}}}}}'

        music_data_response = requests.get(music_data_url,headers=head_search,cookies=cookie)

        data_info = jsonpath(music_data_response.json(), expr='$..purl')[0]

        music_url = f'https://dl.stream.qqmusic.qq.com/{data_info}'

        urls.append(music_url)

    return urls

# import aiohttp
# import asyncio
# import jsonpath_ng as jsonpath
#
#
# async def fetch_url(session, item, cookie):
#     music_data_url = rf'https://u.y.qq.com/cgi-bin/musicu.fcg?data={{"comm":{{"cv":4747474,"ct":24,"format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"yqq.json","needNewCode":1,"uin":"1152921504916411742","g_tk_new_20200303":1849600344,"g_tk":1849600344}},"req_9":{{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{{"guid":"4868259520","songmid":["{item}"],"songtype":[0],"uin":"1152921504916411742","loginflag":1,"platform":"20"}}}}}}'
#
#     async with session.get(music_data_url, headers={
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Accept-Encoding': 'gzip, deflate, sdch',
#         'Accept-Language': 'en-US,en;q=0.8',
#         'Connection': 'keep-alive',
#         'Cookie': cookie,
#     }) as response:
#         response_data = await response.json()
#         data_info = jsonpath.parse('$..purl').find(response_data)[0].value
#         music_url = f'https://dl.stream.qqmusic.qq.com/{data_info}'
#         return music_url
#
#
# async def get_urls(items, cookie):
#     urls = []
#     async with aiohttp.ClientSession() as session:
#         tasks = [fetch_url(session, item, cookie) for item in items]
#         for future in asyncio.as_completed(tasks):
#             url = await future
#             urls.append(url)
#     return urls