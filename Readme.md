# ikuuu 自动签到配置说明

## 配置文件：config.json

### 文件位置
- 开发时：与 `main.py` 在同一目录

### 配置项说明

#### 1. accounts（账号列表）
可以配置多个账号，每个账号包含：
```json
{
  "email": "你的邮箱",
  "password": "你的密码"
}
```

**示例 - 单个账号：**
```json
"accounts": [
  {
    "email": "example@gmail.com",
    "password": "your_password"
  }
]
```

**示例 - 多个账号：**
```json
"accounts": [
  {
    "email": "account1@gmail.com",
    "password": "password1"
  },
  {
    "email": "account2@gmail.com",
    "password": "password2"
  }
]
```

#### 2. urls（网址配置）
```json
"urls": {
  "login": "https://ikuuu.de/auth/login",      // 登录地址
  "checkin": "https://ikuuu.de/user/checkin",  // 签到地址
  "info": "https://ikuuu.de/user/profile"      // 用户信息地址
}
```
⚠️ **重要**：ikuuu 会不定时更换域名，当无法连接时需要更新这里的网址！

#### 3. push（推送配置）
支持两种推送方式，二选一：

**方式1：Server酱（推荐）**
```json
"push": {
  "sckey": "你的Server酱SCKEY",
  "token": "1"
}
```

**方式2：PushPlus**
```json
"push": {
  "sckey": "1",
  "token": "你的PushPlus Token"
}
```

**禁用推送：**
```json
"push": {
  "sckey": "1",
  "token": "1"
}
```

#### 4. proxy（代理配置）
```json
"proxy": {
  "enabled": false,                        // true=启用代理, false=禁用代理
  "http": "http://127.0.0.1:7890",        // HTTP代理地址
  "https": "http://127.0.0.1:7890"        // HTTPS代理地址
}
```

**常见代理端口：**
- Clash: 7890
- V2Ray: 10809
- SSR: 1080

**使用建议：**
- 如果使用全局VPN，设置 `"enabled": false`
- 如果使用本地代理软件，设置 `"enabled": true` 并配置正确的端口

#### 5. settings（其他设置）
```json
"settings": {
  "timeout": 10,                                    // 请求超时时间（秒）
  "user_agent": "Mozilla/5.0 ..."                  // 浏览器标识
}
```

---

## 完整配置示例

```json
{
  "accounts": [
    {
      "email": "your_email@example.com",
      "password": "your_password"
    }
  ],
  "urls": {
    "login": "https://ikuuu.de/auth/login",
    "checkin": "https://ikuuu.de/user/checkin",
    "info": "https://ikuuu.de/user/profile"
  },
  "push": {
    "sckey": "1",
    "token": "1"
  },
  "proxy": {
    "enabled": false,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  },
  "settings": {
    "timeout": 10,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
  }
}
```

---

## 常见问题

### 1. 如何添加多个账号？
在 `accounts` 数组中添加多个对象即可。

### 2. 域名失效怎么办？
更新 `urls` 中的三个网址为最新域名。

### 3. 如何启用推送？
- 获取 Server酱 SCKEY：https://sct.ftqq.com/
- 或获取 PushPlus Token：https://www.pushplus.plus/
- 将获取的值填入 `push` 配置中

### 4. 代理错误怎么办？
- 如果使用VPN，设置 `"enabled": false`
- 如果使用代理软件，确认端口号并设置 `"enabled": true`
