import time
import requests
from jsonpath import jsonpath

def search_and_download_qq_music(query_text):
    head_search = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'Cookie':'pgv_pvid=8718334655; eas_sid=01z7V0V2K110g8G0d6e124h9Z4; RK=N0u1eippPz; ptcz=d26e5e724fe9bcaf18d0c41d98402fe2cc845d4165ef6556c709a5546f5282d9; qq_domain_video_guid_verify=01c5353ed08dd3d9; _qimei_uuid42=1880a0f2d17100420be6318a560c1def8e329c04f1; _qimei_fingerprint=d05ede39451f04ae8211e82eb1a11c2e; _qimei_q36=; _qimei_h38=3968c0f70be6318a560c1def0200000841880a; fqm_pvqid=daaee996-22e7-4f35-b99b-7c1e8627586c; ts_uid=4614304352; euin=ownqowEAoiCP7z**; tmeLoginType=2; music_ignore_pskey=202306271436Hn@vBj; ts_refer=i.y.qq.com/; psrf_musickey_createtime=1732457454; uin=2092923647; psrf_qqaccess_token=FC36343959563742A0FEDD1CFB17DDA4; wxrefresh_token=; psrf_qqopenid=00F03BBF2711E6E57F3022113C288745; psrf_qqrefresh_token=84AC7F106DE7EFA729C610EAE136536F; wxopenid=; wxunionid=; psrf_qqunionid=BF80135E48237BC20A08D84F2AAD00CE; qm_keyst=Q_H_L_63k3Noxa5KMciw03Dw9kyMul_JiULkdFqJfhkRmDsggXJ52niKszuqHSbQ9CYVgaOQz5tVtiKXaqidcK-iaOy6w; psrf_access_token_expiresAt=1733062254; qqmusic_key=Q_H_L_63k3Noxa5KMciw03Dw9kyMul_JiULkdFqJfhkRmDsggXJ52niKszuqHSbQ9CYVgaOQz5tVtiKXaqidcK-iaOy6w; fqm_sessionid=f16d0dea-3a44-4dd8-b3b3-a14879755785; pgv_info=ssid=s7904494745; ts_last=y.qq.com/n/ryqq/search'
    }
    
    search_url = rf'https://u6.y.qq.com/cgi-bin/musicu.fcg?data={{"comm":{{"g_tk":1450558827,"uin":"1152921504916411742","format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"h5","needNewCode":1,"ct":23,"cv":0}},"req_0":{{"method":"DoSearchForQQMusicDesktop","module":"music.search.SearchCgiService","param":{{"remoteplace":"txt.mqq.all","searchid":"65573365980118679","search_type":0,"query":"{query_text}","page_num":1,"num_per_page":20}}}}}}'

    #print(search_url)

    response = requests.get(search_url,headers=head_search)
    #print(response.text)
    music_list = jsonpath(response.json(), '$..data.body.song.list')[0]
    print(music_list)

    flag=int(0)
    for item in music_list:
        music_mid = jsonpath(item, '$.mid')[0]
        music_name = jsonpath(item, '$.name')[0]
        music_title = jsonpath(item, '$.title')[0]
        singer_name = jsonpath(item, '$.singer')[0][0]['name']
        singer_title = jsonpath(item, '$.singer')[0][0]['title']

        print(f'{flag+1}:music_name: {music_name}, music_mid: {music_mid} , music_title:{music_title},singer_name:{singer_name},singer_title:{singer_title}')

        music_data_url = rf'https://u.y.qq.com/cgi-bin/musicu.fcg?data={{"comm":{{"cv":4747474,"ct":24,"format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"yqq.json","needNewCode":1,"uin":"1152921504916411742","g_tk_new_20200303":1849600344,"g_tk":1849600344}},"req_9":{{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{{"guid":"4868259520","songmid":["{music_mid}"],"songtype":[0],"uin":"1152921504916411742","loginflag":1,"platform":"20"}}}}}}'

        music_data_response = requests.get(music_data_url,headers=head_search)
        #print(f'music_data_response: {music_data_response.json()}')

        data_info = jsonpath(music_data_response.json(), '$..purl')[0]
        # print(f'data_info: {data_info}')

        music_url = f'https://dl.stream.qqmusic.qq.com/{data_info}'
        print(flag+1,':',music_url)

        #music_response = requests.get(music_url, headers=head)
        # with open(f'./Q Music/{music_name}.mp3', 'wb') as file:
        #     file.write(music_response.content)
        # print(f'《{music_name}》下载成功')

        print("-" * 30)
        time.sleep(1)
        flag=flag+1
        if flag==6:
            break

song=input('搜索：')

search_and_download_qq_music(song)

