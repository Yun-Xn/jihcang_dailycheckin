import requests, json, re, os
import socket
import ssl
from urllib.parse import urlparse
import sys

# ==================== 加载配置文件 ====================
def load_config():
    """加载配置文件"""
    config_file = 'config.json'
    
    # 支持打包后的exe文件
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe，配置文件在exe同目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 如果是python脚本，配置文件在脚本同目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    config_path = os.path.join(base_path, config_file)
    
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        print(f'错误: 找不到配置文件 {config_path}')
        print('请确保 config.json 文件与程序在同一目录下')
        input('按任意键退出...')
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f'✓ 成功加载配置文件: {config_path}')
            return config
    except json.JSONDecodeError as e:
        print(f'错误: 配置文件格式错误')
        print(f'详情: {str(e)}')
        input('按任意键退出...')
        sys.exit(1)
    except Exception as e:
        print(f'错误: 无法读取配置文件')
        print(f'详情: {str(e)}')
        input('按任意键退出...')
        sys.exit(1)

# 加载配置
config = load_config()

session = requests.session()

# 网络诊断函数
def diagnose_connection(url):
    """诊断网络连接问题"""
    diagnosis = []
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split('/')[0]
    
    # 1. DNS解析测试
    try:
        ip_address = socket.gethostbyname(domain)
        diagnosis.append(f"✓ DNS解析成功: {domain} -> {ip_address}")
    except socket.gaierror as e:
        diagnosis.append(f"✗ DNS解析失败: {domain}")
        diagnosis.append(f"  错误: {str(e)}")
        diagnosis.append(f"  可能原因: 域名不存在或DNS服务器无法访问")
        return "\n".join(diagnosis)
    
    # 2. TCP连接测试
    port = 443 if parsed.scheme == 'https' else 80
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip_address, port))
        sock.close()
        if result == 0:
            diagnosis.append(f"✓ TCP连接成功: {ip_address}:{port}")
        else:
            diagnosis.append(f"✗ TCP连接失败: {ip_address}:{port}")
            diagnosis.append(f"  错误代码: {result}")
            diagnosis.append(f"  可能原因: 端口被封锁或服务器未响应")
            return "\n".join(diagnosis)
    except Exception as e:
        diagnosis.append(f"✗ TCP连接测试异常: {str(e)}")
        return "\n".join(diagnosis)
    
    # 3. SSL/TLS握手测试（仅HTTPS）
    if parsed.scheme == 'https':
        try:
            context = ssl.create_default_context()
            with socket.create_connection((ip_address, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    diagnosis.append(f"✓ SSL/TLS握手成功")
                    diagnosis.append(f"  协议版本: {ssock.version()}")
        except ssl.SSLError as e:
            diagnosis.append(f"✗ SSL/TLS握手失败")
            diagnosis.append(f"  错误: {str(e)}")
            diagnosis.append(f"  可能原因: 证书无效或SSL协议不匹配")
            return "\n".join(diagnosis)
        except Exception as e:
            diagnosis.append(f"✗ SSL测试异常: {str(e)}")
            return "\n".join(diagnosis)
    
    return "\n".join(diagnosis)

# ==================== 从配置文件读取设置 ====================
# 获取账号列表
accounts = config.get('accounts', [])
if not accounts:
    print('错误: 配置文件中没有账号信息')
    input('按任意键退出...')
    sys.exit(1)

# 获取URL配置
urls = config.get('urls', {})
login_url = urls.get('login', 'https://ikuuu.de/auth/login')
check_url = urls.get('checkin', 'https://ikuuu.de/user/checkin')
info_url = urls.get('info', 'https://ikuuu.de/user/profile')

# 获取推送配置
push_config = config.get('push', {})
SCKEY = push_config.get('sckey', '1')
Token = push_config.get('token', '1')

# 获取代理配置
proxy_config = config.get('proxy', {})
USE_PROXY = proxy_config.get('enabled', False)
CUSTOM_PROXY = {
    'http': proxy_config.get('http', 'http://127.0.0.1:7890'),
    'https': proxy_config.get('https', 'http://127.0.0.1:7890')
}

# 获取其他设置
settings = config.get('settings', {})
TIMEOUT = settings.get('timeout', 10)
USER_AGENT = settings.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')

# 从URL中提取域名作为origin
from urllib.parse import urlparse
parsed_url = urlparse(login_url)
origin = f"{parsed_url.scheme}://{parsed_url.netloc}"

header = {
    'origin': origin,
    'user-agent': USER_AGENT
}

def push(content):
    """消息推送函数"""
    if SCKEY != '1':
        url = "https://sctapi.ftqq.com/{}.send?title={}&desp={}".format(SCKEY, 'ikuuu签到', content)
        requests.post(url)
        print('推送完成')
    elif Token != '1':
        headers = {'Content-Type': 'application/json'}
        push_json = {"token": Token, 'title': 'ikuuu签到', 'content': content, "template": "json"}
        resp = requests.post(f'http://www.pushplus.plus/send', json=push_json, headers=headers).json()
        print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')
    else:
        print('未使用消息推送推送！')

print(f'\n========== ikuuu 自动签到 ===========')
print(f'配置的账号数量: {len(accounts)}')
print(f'登录URL: {login_url}')
print(f'代理设置: {"启用" if USE_PROXY else "禁用"}')
print(f'===================================\n')

# 遍历所有账号进行签到
for idx, account in enumerate(accounts, 1):
    email = account.get('email')
    passwd = account.get('password')
    
    if not email or not passwd:
        print(f'[警告] 第{idx}个账号配置不完整，跳过')
        continue
    
    print(f'\n--- 处理第 {idx}/{len(accounts)} 个账号 ---')
    
    session = requests.session()
    
    # 配置代理设置
    if not USE_PROXY:
        # 禁用所有代理（包括系统代理）
        session.trust_env = False
        print(f'[信息] 已禁用代理，直连模式')
    else:
        # 使用自定义代理
        session.proxies.update(CUSTOM_PROXY)
        print(f'[信息] 使用自定义代理: {CUSTOM_PROXY["https"]}')
    
    data = {
        'email': email,
        'passwd': passwd
    }
    try:
        print(f'[{email}] 进行登录...')
        login_response = session.post(url=login_url, headers=header, data=data, timeout=TIMEOUT)
        login_response.raise_for_status()  # 检查HTTP状态码
        response = json.loads(login_response.text)
        print(response['msg'])
        
        # 获取账号名称
        # info_html = session.get(url=info_url,headers=header).text
        # info = "".join(re.findall('<span class="user-name text-bold-600">(.*?)</span>', info_html, re.S))
        
        # 进行签到
        checkin_response = session.post(url=check_url, headers=header, timeout=TIMEOUT)
        checkin_response.raise_for_status()  # 检查HTTP状态码
        result = json.loads(checkin_response.text)
        print(result['msg'])
        content = result['msg']
        # 进行推送
        push(content)
    except requests.exceptions.SSLError as e:
        # SSL证书错误
        error_msg = f'【{email}】签到失败 - SSL证书错误\n'
        error_msg += f'错误详情: {str(e)}\n'
        error_msg += f'可能原因:\n'
        error_msg += f'  1. 服务器SSL证书已过期或无效\n'
        error_msg += f'  2. 系统时间不正确\n'
        error_msg += f'  3. 缺少根证书\n'
        error_msg += f'\n开始网络诊断...\n'
        error_msg += diagnose_connection(login_url)
        print(error_msg)
        push(error_msg)
    except requests.exceptions.ConnectionError as e:
        # 连接错误 - 进行详细诊断
        error_msg = f'【{email}】签到失败 - 连接错误\n'
        error_msg += f'原始错误: {str(e)}\n'
        
        # 检查是否是代理错误
        if 'ProxyError' in str(e) or 'proxy' in str(e).lower():
            error_msg += f'\n⚠️ 检测到代理错误！\n'
            error_msg += f'当前代理设置: USE_PROXY={USE_PROXY}\n'
            if USE_PROXY:
                error_msg += f'自定义代理: {CUSTOM_PROXY}\n'
            error_msg += f'\n解决方案:\n'
            error_msg += f'  1. 【推荐】修改代码中的 USE_PROXY = False（禁用代理，使用VPN直连）\n'
            error_msg += f'  2. 或者修改 CUSTOM_PROXY 为正确的代理地址和端口\n'
            error_msg += f'  3. 检查你的VPN/代理软件是否正常运行\n'
            error_msg += f'  4. 如果使用Clash/V2Ray，确认代理端口（常见: 7890/10809/1080）'
        else:
            error_msg += f'\n开始网络诊断...\n'
            error_msg += diagnose_connection(login_url)
            error_msg += f'\n\n可能的解决方案:\n'
            error_msg += f'  1. 检查域名是否已更新（ikuuu经常更换域名）\n'
            error_msg += f'  2. 检查网络连接是否正常\n'
            error_msg += f'  3. 尝试使用代理或VPN\n'
            error_msg += f'  4. 检查防火墙设置\n'
            error_msg += f'  5. 更换DNS服务器（如8.8.8.8或1.1.1.1）'
        print(error_msg)
        push(error_msg)
    except requests.exceptions.Timeout as e:
        # 超时错误
        error_msg = f'【{email}】签到失败 - 请求超时\n'
        error_msg += f'错误详情: {str(e)}\n'
        error_msg += f'可能原因:\n'
        error_msg += f'  1. 网络延迟过高\n'
        error_msg += f'  2. 服务器响应缓慢\n'
        error_msg += f'  3. 被防火墙限制\n'
        error_msg += f'\n开始网络诊断...\n'
        error_msg += diagnose_connection(login_url)
        print(error_msg)
        push(error_msg)
    except requests.exceptions.HTTPError as e:
        # HTTP错误
        error_msg = f'【{email}】签到失败 - HTTP错误\n'
        error_msg += f'状态码: {e.response.status_code}\n'
        if e.response.status_code == 403:
            error_msg += f'403 Forbidden - 可能被服务器拒绝访问，IP可能被封禁\n'
        elif e.response.status_code == 404:
            error_msg += f'404 Not Found - 页面不存在，API路径可能已变更\n'
        elif e.response.status_code == 500:
            error_msg += f'500 Internal Server Error - 服务器内部错误\n'
        elif e.response.status_code == 502:
            error_msg += f'502 Bad Gateway - 网关错误，服务器可能暂时不可用\n'
        elif e.response.status_code == 503:
            error_msg += f'503 Service Unavailable - 服务不可用，服务器可能维护中\n'
        try:
            error_detail = e.response.text[:300]
            error_msg += f'\n响应内容: {error_detail}\n'
            error_msg += f'响应头: {dict(e.response.headers)}'
        except:
            pass
        print(error_msg)
        push(error_msg)
    except requests.exceptions.RequestException as e:
        # 其他网络请求错误
        error_msg = f'【{email}】签到失败 - 网络请求错误\n'
        error_msg += f'错误类型: {type(e).__name__}\n'
        error_msg += f'错误详情: {str(e)}\n'
        error_msg += f'\n开始网络诊断...\n'
        error_msg += diagnose_connection(login_url)
        print(error_msg)
        push(error_msg)
    except json.JSONDecodeError as e:
        # JSON解析错误
        error_msg = f'【{email}】签到失败 - JSON解析错误\n错误详情: {str(e)}\n可能原因: 服务器返回的不是有效的JSON格式'
        print(error_msg)
        push(error_msg)
    except KeyError as e:
        # 字典键错误
        error_msg = f'【{email}】签到失败 - 响应数据格式错误\n缺少字段: {str(e)}\n可能原因: API返回格式已变更或登录失败'
        print(error_msg)
        push(error_msg)
    except Exception as e:
        # 其他未知错误
        error_msg = f'【{email}】签到失败 - 未知错误\n错误类型: {type(e).__name__}\n错误详情: {str(e)}'
        print(error_msg)
        push(error_msg)
