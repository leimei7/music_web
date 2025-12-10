import requests
head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}
for start in range(0,10):
    response=requests.get(f'https://wap.faloo.com/1422416_{start}.html',headers=head)
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(response.text,'html.parser')
    p=soup.findAll('p')
    for i in p:
        print(i.string)#去掉标签
response.close()