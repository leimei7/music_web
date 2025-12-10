# Flask 音乐网站核心模块 - README

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-2.0%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 一、模块介绍
该文件是基于 Flask 框架开发的音乐网站核心业务模块，实现了音乐搜索、收藏、下载、QQ 扫码登录获取 U_key、用户权限控制等核心功能，通过 Blueprint 组织路由，集成第三方音乐接口完成音乐资源的检索与播放链接获取。

## 二、核心功能列表
| 功能分类       | 具体功能                     | 路由地址               | 请求方式 | 权限要求       |
|----------------|------------------------------|------------------------|----------|----------------|
| 页面访问       | 首页/核心入口                | `/`/`/index/`          | GET      | 登录后访问     |
| 页面访问       | 收藏列表（分页）             | `/collect/<int:page>/` | GET      | 登录后访问     |
| 页面访问       | 下载页                       | `/download/`           | GET      | 登录后访问     |
| 页面访问       | 系统设置页                   | `/admin/`              | GET/POST | 登录后访问     |
| 页面访问       | 登录页                       | `/login/`              | GET/POST | 无需登录       |
| 页面访问       | 升级页                       | `/upgrade/`            | GET      | 登录后访问     |
| 页面访问       | 抖音/小说等分类页            | `/titok/`/`/book/`     | GET      | 登录后访问     |
| 音乐操作       | 音乐搜索                     | `/select/`             | GET/POST | 登录后访问     |
| 音乐操作       | 添加收藏                     | `/favorite/`           | POST     | 登录后访问     |
| 音乐操作       | 取消收藏                     | `/delete/`             | POST/GET | 登录后访问     |
| 登录相关       | 获取 QQ 登录二维码           | `/newlogin/qrcode/`    | GET      | 登录后访问     |
| 登录相关       | 检测 QQ 扫码登录状态         | `/newlogin/check_status/` | GET   | 登录后访问     |

## 三、技术栈与依赖
### 1. 核心依赖
| 依赖库         | 版本要求       | 功能用途                     |
|----------------|----------------|------------------------------|
| Flask          | 2.0+           | Web 框架，实现路由/模板/会话  |
| requests       | 2.28+          | 发送 HTTP 请求（QQ 登录/音乐接口） |
| urllib3        | 1.26+          | HTTP 请求优化，忽略 SSL 警告 |
| hashlib        | 内置           | MD5 密码加密                 |
| threading      | 内置           | 异步检测 QQ 扫码状态         |
| base64         | 内置           | 二维码图片 Base64 编码       |
| re             | 内置           | 正则提取 QQ 登录凭证         |
| functools      | 内置           | 装饰器实现登录权限控制       |
| SQLAlchemy     | 2.0+           | 数据库 ORM（操作 SetData/MSelect 模型） |
| Flask-Cache    | 2.0+           | 收藏列表缓存优化             |

### 2. 第三方接口依赖
- 音乐搜索接口：`music_api.py` 中的 `search_music` 函数
- 播放链接获取接口：`urls_api.py` 中的 `get_urls` 函数
- QQ 登录授权码获取：`get_code.py` 中的 `get_authorization_url` 函数
- U_key 兑换接口：`get_key.py` 中的 `post_request` 函数

## 四、核心函数说明
### 1. 权限控制装饰器
```python
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login/')
        return f(*args, **kwargs)
    return wrapper
```
- 功能：校验用户登录状态，未登录用户重定向到登录页
- 使用场景：所有需要登录后访问的路由函数装饰

### 2. MD5 密码加密函数
```python
def md5_key(string):
    md5_obj=hashlib.md5()  # 创建 MD5 对象
    md5_obj.update(string.encode('utf-8'))  # 传入文本更新对象
    value=md5_obj.hexdigest()  # 获取 32 位加密结果
    return value
```
- 功能：对用户密码进行 MD5 加密存储/验证
- 入参：待加密字符串
- 返回：32 位 MD5 加密结果

### 3. QQ 登录核心函数
#### (1) 生成登录二维码
```python
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
```
- 功能：调用 QQ 登录接口生成二维码，返回 Base64 编码结果
- 返回：Base64 格式的二维码字符串

#### (2) 检测扫码状态
```python
def check_qrcode_status():
    global login_status, session2
    ptqrlogin_url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?'
    while True:
        # 构造请求参数（省略）
        response = session2.get(ptqrlogin_url, params=params)
        if '二维码未失效' in response.text:
            login_status = {'success': False, 'message': '等待登录'}
        elif '正在登录' in response.text:
            login_status = {'success': False, 'message': "正在登录"}
        elif '二维码已经失效' in response.text:
            login_status = {'success': True, 'message': '二维码已经失效'}
            session2 = requests.Session()
            break
        elif '成功' in response.text:
            final_session2 = finalize_login(response)
            mkey = final_final(final_session2.cookies)
            login_status = {'success': True, 'message': "登录成功" }
            session2 = requests.Session()
            break
        else:
            login_status = {'success': True, 'message': str(response.text) }
            session2 = requests.Session()
            break
        time.sleep(1)
```
- 功能：异步循环检测二维码扫码状态，成功后自动兑换 U_key
- 状态：等待登录/正在登录/二维码失效/登录成功

#### (3) U_key 提取与兑换
```python
def final_final(cookies):
    params = ['p_skey', 'pt4_token', 'pt_oauth_token', 'p_uin']
    extracted_params = {}
    for cookie in cookies:
        if cookie.name in params:
            extracted_params[cookie.name] = cookie.value
    p_skey = extracted_params.get('p_skey')
    pt4_token = extracted_params.get('pt4_token')
    pt_oauth_token = extracted_params.get('pt_oauth_token')
    p_uin = extracted_params.get('p_uin')
    g_tk = calculate_g_tk(p_skey)
    code = get_authorization_url(p_skey, pt4_token, pt_oauth_token, p_uin, g_tk)
    m_key = post_request(g_tk, code)
    return m_key
```
- 功能：从登录成功的 Cookie 中提取参数，计算 g_tk 并兑换 U_key
- 入参：QQ 登录成功后的 Cookie 列表
- 返回：兑换后的 U_key

### 4. 收藏列表分页函数
```python
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
    items=[i.mid for i in musics]
    numbers=range(len(items))
    key = SetData.query.first().U_key
    urls = get_urls(items, key)
    return render_template('collect.html',name=SetData.query.first().name,theme=SetData.query.first().theme,urls=urls,musics=musics,numbers=numbers,page=pg,pages=pages)
```
- 功能：分页查询收藏的音乐，缓存 5 秒减少数据库压力
- 入参：页码 page
- 返回：渲染后的收藏列表页面

## 五、全局变量说明
| 变量名         | 类型          | 功能说明                     |
|----------------|---------------|------------------------------|
| session2       | requests.Session | QQ 登录专用请求会话         |
| headers        | dict          | 请求头（模拟浏览器）|
| login_status   | dict          | QQ 登录状态（success/message） |
| pt_login_sig   | str/None      | QQ 登录签名                  |
| ptqrtoken      | int/None      | 二维码 Token                 |
| mkey           | str           | 兑换后的 U_key               |

## 六、使用说明
### 1. 环境准备
```bash
# 安装核心依赖
pip install flask requests urllib3 sqlalchemy flask-cache
```

### 2. 模块集成
```python
# 在 Flask 主应用中注册蓝图
from app.music import blue

app = Flask(__name__)
app.register_blueprint(blue)

# 配置会话密钥（必填）
app.secret_key = 'your-secret-key'

# 配置缓存（可选）
app.config['CACHE_TYPE'] = 'simple'
```

### 3. 数据库初始化
确保 `modles.py` 中定义了以下模型：
- `SetData`：系统配置模型（存储 U_key/用户名/主题/密码等）
- `MSelect`：音乐收藏模型（存储 name/singer/mid 等）

```python
# 初始化数据库表
from app.exts import db
db.create_all()

# 添加默认配置
default_set = SetData(
    name="默认用户",
    passwd=md5_key("123456"),  # 默认密码 123456
    flag=6,
    U_key="",
    theme="light"
)
db.session.add(default_set)
db.session.commit()
```

### 4. 启动应用
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 七、注意事项
1. **U_key 有效期**：U_key 存在时效性，需定期通过 QQ 扫码重新获取；
2. **缓存机制**：收藏列表缓存 5 秒，修改收藏后需等待缓存过期；
3. **SSL 警告**：已通过 `urllib3.disable_warnings` 忽略 SSL 警告，生产环境建议启用证书验证；
4. **异常处理**：收藏/取消收藏功能已添加异常捕获和事务回滚，确保数据安全；
5. **登录安全**：密码采用 MD5 加密存储，建议生产环境增加加盐处理；
6. **异步任务**：QQ 扫码状态检测使用线程异步执行，避免阻塞主线程。

## 八、待优化项
- [ ] 增加 U_key 过期自动重新获取机制；
- [ ] 优化缓存策略，支持手动清理缓存；
- [ ] 增加音乐播放进度条和歌词显示功能；
- [ ] 支持批量收藏/取消收藏操作；
- [ ] 完善日志记录，便于问题排查；
- [ ] 增加接口限流，防止恶意请求。

## 九、许可证
本模块采用 MIT 许可证，可自由修改、分发和商用，需保留原作者信息。
