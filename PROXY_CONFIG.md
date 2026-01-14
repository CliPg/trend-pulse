# YouTube API 连接问题解决方案

## 问题描述

在中国大陆访问 Google API (包括 YouTube Data API) 会遇到连接超时问题：

```
❌ YouTube collection failed: Connection timeout to host https://www.googleapis.com/youtube/v3/search
```

## 解决方案

### 方案 1: 配置代理（推荐）

如果你有代理服务器（如 Clash、V2Ray 等），可以配置环境变量：

#### 1. 找到你的代理地址

常见代理软件默认端口：
- **Clash**: `127.0.0.1:7890`
- **V2Ray**: `127.0.0.1:10809`
- **Shadowsocks**: `127.0.0.1:1080`

#### 2. 在 `.env` 文件中添加代理配置

```bash
cd backend
nano .env  # 或使用任何文本编辑器
```

添加以下内容：

```env
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

**注意**: 将 `7890` 替换为你的代理实际端口。

#### 3. 重启后端服务

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python -m src.api.main
```

### 方案 2: 仅使用 Reddit（快速开始）

如果暂时无法配置代理，可以只使用 Reddit 进行数据分析：

修改 `frontend/lib/screens/dashboard_screen.dart` 中的平台配置：

```dart
final result = await ApiService().analyzeKeyword(
  keyword: _keywordController.text,
  language: "en",
  platforms: ["reddit"],  // 只使用 Reddit
  limitPerPlatform: 50,
);
```

或者修改后端配置，在分析时跳过 YouTube：

在 `backend/src/orchestrator.py` 中：

```python
# Default to all platforms
if platforms is None:
    platforms = ["reddit"]  # 只使用 Reddit
    # Twitter 仍然可以尝试
    if self.twitter_collector:
        platforms.append("twitter")
```

### 方案 3: 使用备用 API（高级）

如果你有其他方式访问 YouTube API，可以：

#### 1. 使用反代服务

某些服务提供 Google API 的反向代理：
- 在 `youtube.py` 中修改 `base_url`
- 替换为可访问的镜像地址

#### 2. 使用 VPN

在系统级别配置 VPN，然后让 Python 自动使用系统代理。

## 验证配置

### 测试代理是否生效

运行 Python 测试脚本：

```python
import os
import asyncio
import aiohttp

async def test_youtube_api():
    proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
    timeout = aiohttp.ClientTimeout(total=60, connect=30)

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": "test",
        "type": "video",
        "maxResults": 1,
        "key": "YOUR_API_KEY"
    }

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params, proxy=proxy) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    print("✅ YouTube API 连接成功！")
                    data = await response.json()
                    print(f"Found {len(data.get('items', []))} videos")
                else:
                    print(f"❌ API Error: {await response.text()}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

asyncio.run(test_youtube_api())
```

### 测试完整流程

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量（临时）
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 测试 API
python -m src.api.main
```

在 Flutter 中测试关键词，观察 YouTube 是否能成功采集。

## 常见代理软件配置

### Clash

1. 打开 Clash
2. 查看"端口设置" → "HTTP 代理端口"（默认 7890）
3. 在 `.env` 中添加：
   ```env
   HTTP_PROXY=http://127.0.0.1:7890
   HTTPS_PROXY=http://127.0.0.1:7890
   ```

### V2Ray

1. 打开 V2Ray
2. 查看"参数设置" → "HTTP 代理端口"（默认 10809）
3. 在 `.env` 中添加：
   ```env
   HTTP_PROXY=http://127.0.0.1:10809
   HTTPS_PROXY=http://127.0.0.1:10809
   ```

### Shadowsocks

1. 打开 Shadowsocks
2. 启用"允许来自局域网的连接"
3. 查看"本地端口"（默认 1080）
4. 在 `.env` 中添加：
   ```env
   HTTP_PROXY=http://127.0.0.1:1080
   HTTPS_PROXY=http://127.0.0.1:1080
   ```

## 注意事项

### 1. 代理必须保持运行

在使用 TrendPulse 期间，代理软件必须保持运行状态。

### 2. 端口号可能不同

不同软件的默认端口不同，请根据实际配置调整。

### 3. 防火墙设置

确保防火墙允许 Python 访问网络。

### 4. API 配额

YouTube API 有每日配额限制（10,000 单位/天）：
- 每次搜索消耗 100 单位
- 大约可以搜索 100 次
- 配额每天午夜太平洋时间重置

## 代码改进

我已经对代码进行了以下改进：

### 1. 增加超时时间

```python
self.timeout = aiohttp.ClientTimeout(
    total=60,    # 总超时 60 秒
    connect=30,  # 连接超时 30 秒
    sock_read=30 # 读取超时 30 秒
)
```

### 2. 自动读取代理

```python
self.proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
```

### 3. 更好的错误处理

```python
except asyncio.TimeoutError:
    print("⏱️  YouTube API timeout - check your network connection or proxy")
    return []
```

### 4. 优雅降级

如果 YouTube API 连接失败，系统会：
- 继续使用 Reddit 数据
- 继续使用 Twitter 数据（如果配置）
- 不会导致整个分析失败

## 不使用 YouTube 的替代方案

如果你不想配置代理，也可以只使用 Reddit：

### 修改 Flutter 代码

在 `frontend/lib/screens/dashboard_screen.dart` 中：

```dart
final result = await ApiService().analyzeKeyword(
  keyword: _keywordController.text,
  language: "en",
  platforms: ["reddit", "twitter"],  // 移除 "youtube"
  limitPerPlatform: 50,
);
```

这样可以：
- ✅ 避免代理配置
- ✅ 仍然获得 20/30 分的数据采集分数
- ✅ Reddit 数据质量通常也很高

## 总结

**推荐方案**：配置代理 → 使用全部 3 个平台 → 获最高分 (30/30)

**快速方案**：只用 Reddit → 20/30 分 → 节省时间

选择适合你的方案即可！ 🚀
