# AKShare 请求层架构改造方案

## 第一步：技术框架与可行性分析

### 1.1 现状诊断

**核心请求层（2 个入口点）**:
- `akshare/utils/request.py` — `request_with_retry()`: 每次请求创建全新 Session，无浏览器伪装，无 Cookie 管理
- `akshare/request.py` — `make_request_with_retry_json/text()`: 使用裸 `requests.get()`，无 Session 复用

**上层包装器**:
- `akshare_pro.py` 中的 `_BrowserSession` 和 `AKSharePro` 已有较好的浏览器伪装，但通过猴子补丁（monkey-patch）实现，侵入性强
- `akshare/utils/context.py` 中的 `AkshareConfig` 单例已有 `proxies` 支持，但功能单一

**各数据模块**: 500+ 接口各自独立调用 `requests.get/post`，部分硬编码了 headers（如 `stock_zh_a_sina.py`、`bond_china_money.py`、`stock_xq.py`）

### 1.2 核心问题

| 问题 | 影响 |
|------|------|
| 无浏览器级请求伪装 | 易被各站反爬识别，封 IP |
| 无全局 Session/Cookie 管理 | 用户无法传递浏览器登录后的 Cookie |
| 每次请求新建连接 | 无法复用 TCP 连接，效率低 |
| 无统一进度回调 | 上层应用无法感知数据获取进度 |
| 断点续传仅在 akshare_pro.py | 核心库无此能力 |

### 1.3 技术方案

**核心思路**: 在 `AkshareConfig` 单例中扩展全局请求配置，在 `request_with_retry()` 中统一消费，保持所有接口零修改即获得增强能力。

```
用户代码
    |
    v
akshare.xxx()  (500+ 接口，无需修改)
    |
    v
akshare/utils/request.py  request_with_retry()  <-- 改造核心
    |
    v
akshare/utils/context.py  AkshareConfig  <-- 扩展配置
    |
    v
BrowserSessionManager  <-- 新增：浏览器会话管理器
    ├── 浏览器级请求头（per-host）
    ├── Cookie/Session 注入
    ├── 进度回调
    ├── 断点续传
    └── 智能限频
```

**兼容性保证**: 所有新参数均有默认值，现有接口无需任何修改即可工作。用户通过新的公共 API（如 `ak.set_cookies()`）按需启用增强功能。

---

## 第二步：任务分解

### Task 1: 扩展 AkshareConfig 全局配置（`akshare/utils/context.py`）

在现有 `AkshareConfig` 单例中新增以下配置项：
- `cookies`: 用户自定义 Cookie（dict 或 str）
- `session`: 用户自定义 requests.Session 实例
- `browser_headers`: per-host 浏览器请求头模板
- `progress_callback`: 全局进度回调函数 `Callable[[int, str], None]`
- `rate_limit`: 智能限频配置（per-host 延迟范围）
- `checkpoint_enabled`: 是否启用断点续传
- `checkpoint_dir`: 断点状态保存目录

新增公共 API 函数：
- `set_cookies(cookies)` / `get_cookies()`
- `set_session(session)` / `get_session()`
- `set_progress_callback(callback)` / `get_progress_callback()`
- `set_rate_limit(host, min_delay, max_delay)`
- `BrowserCookieContext` 上下文管理器

### Task 2: 实现 BrowserSessionManager（`akshare/utils/session.py` — 新文件）

核心职责：
- 维护 per-host 浏览器级请求头（从 `akshare_pro.py` 的 `HOST_HEADERS` 迁移并增强）
- 管理全局 Session 实例（连接池复用）
- 自动注入 Cookie/Headers
- 智能限频（per-host 独立限频策略）
- TLS 指纹伪装（使用 `curl_cffi` 可选）

```python
class BrowserSessionManager:
    def get_session(self) -> requests.Session
    def get_headers(self, url: str) -> dict
    def inject_cookies(self, url: str, cookies: dict)
    def rate_limit_wait(self, url: str)
```

### Task 3: 改造 request_with_retry（`akshare/utils/request.py`）

增强 `request_with_retry()` 函数：
- 使用 `BrowserSessionManager` 提供的 Session 和 Headers
- 支持从全局 config 读取用户注入的 Cookie
- 支持进度回调（通过 config 获取）
- 支持可选的断点续传参数
- 新增可选参数：`cookies`, `progress_callback`, `resume_key`

**保持向后兼容**：所有新参数默认为 None，从全局 config 获取。

### Task 4: 改造 make_request_with_retry（`akshare/request.py`）

同步改造，使其使用 `BrowserSessionManager`，保持与 `request_with_retry` 一致的行为。

### Task 5: 在 `akshare/__init__.py` 中导出新 API

导出以下公共函数：
```python
from akshare.utils.context import (
    set_cookies, get_cookies,
    set_session, get_session,
    set_progress_callback, get_progress_callback,
    set_rate_limit,
)
```

### Task 6: 重构 akshare_pro.py（`/Users/admin/codes/qlib/QuantByQlib/services/akshare_pro.py`）

- 移除猴子补丁方式，改用核心库的新 API
- `_BrowserSession` 的功能迁移到核心库的 `BrowserSessionManager`
- `AKSharePro` 简化为配置包装器，使用 `ak.set_cookies()` / `ak.set_session()` 等新 API
- `fetch_paginated_data_with_resume` 的断点续传逻辑迁移到核心库

### Task 7: 更新 qlib_instruments_updater.py

- 适配新的 `AKSharePro` 接口
- 使用核心库的进度回调和断点续传

### Task 8: 编写测试

- 测试 BrowserSessionManager 的请求头注入
- 测试 Cookie 注入和 Session 复用
- 测试断点续传
- 测试进度回调
- 测试与现有接口的兼容性

### Task 9: 更新帮助文档

- 更新 `docs/akshare_help_summary.md` 添加新功能说明
- 新增使用示例文档

---

## 第三步：技术改造详细设计

### 3.1 AkshareConfig 扩展

```python
# akshare/utils/context.py
class AkshareConfig:
    # ... 现有代码 ...
    
    def __init__(self):
        self.proxies = None
        self.cookies = {}          # 新增：全局 Cookie
        self.session = None        # 新增：用户自定义 Session
        self.progress_callback = None  # 新增：进度回调
        self.rate_limits = {}      # 新增：per-host 限频配置
        self.checkpoint_enabled = False
        self.checkpoint_dir = "./akshare_checkpoints"
        self._session_manager = None  # 延迟初始化
```

### 3.2 BrowserSessionManager 设计

```python
# akshare/utils/session.py
class BrowserSessionManager:
    """全局浏览器会话管理器（单例）"""
    
    HOST_HEADERS = { ... }  # 从 akshare_pro.py 迁移
    
    def get_session(self) -> requests.Session:
        """获取全局复用的 Session"""
        
    def get_headers(self, url: str) -> dict:
        """根据 URL host 返回浏览器级请求头"""
        
    def merge_user_cookies(self, url: str) -> dict:
        """合并用户注入的 Cookie"""
        
    def wait_if_needed(self, url: str):
        """per-host 智能限频"""
```

### 3.3 request_with_retry 增强

```python
# akshare/utils/request.py
def request_with_retry(
    url: str,
    params: Dict = None,
    timeout: int = 15,
    max_retries: int = 3,
    base_delay: float = 1.0,
    random_delay_range: Tuple[float, float] = (0.5, 1.5),
    # --- 新增参数（全部可选，默认从全局 config 获取）---
    cookies: Dict = None,           # 覆盖全局 Cookie
    progress_callback: Callable = None,  # 覆盖全局回调
    resume_key: str = None,         # 断点续传标识
    session: requests.Session = None,  # 覆盖全局 Session
) -> requests.Response:
```

### 3.4 用户 API 示例

```python
import akshare as ak

# 方式1: 注入浏览器 Cookie（用户在浏览器登录后导出 Cookie）
ak.set_cookies({"xq_a_token": "xxx", "u": "xxx"})  # 雪球 Cookie
ak.set_cookies({"cookie_name": "value"}, host="xueqiu.com")  # per-host

# 方式2: 注入自定义 Session（高级用法）
import requests
s = requests.Session()
s.headers.update({"Authorization": "Bearer xxx"})
ak.set_session(s)

# 方式3: 设置进度回调
def on_progress(pct: int, msg: str):
    print(f"[{pct}%] {msg}")
ak.set_progress_callback(on_progress)

# 方式4: 设置限频
ak.set_rate_limit("eastmoney.com", min_delay=1.0, max_delay=3.0)

# 然后正常使用，无需修改任何代码
df = ak.stock_zh_a_hist(symbol="000001", period="daily")
```

---

## 第四步：验证方案

### 4.1 测试矩阵

| 测试项 | 验证点 |
|--------|--------|
| 无配置直接调用 | 与改造前行为一致（回归测试） |
| 注入 Cookie 后请求 | Cookie 正确出现在请求头中 |
| Session 复用 | 多次调用使用同一 Session 连接 |
| 浏览器请求头 | 发送的 headers 与 Chrome 一致 |
| per-host 限频 | 东财请求间隔 1.5-3s，其他 0.5-1.5s |
| 进度回调 | 回调被正确触发 |
| 断点续传 | 中断后重启从断点继续 |
| 上下文管理器 | 退出 with 块后恢复原配置 |

### 4.2 验证报告模板

```
验证报告
- 测试环境: Python 版本, 系统, akshare 版本
- 回归测试: 500+ 接口中抽样 10 个核心接口
- 新功能测试: Cookie 注入, Session 复用, 进度回调, 断点续传
- 性能对比: 改造前后获取 100 页数据的耗时
- 兼容性: 确认所有现有接口无需修改
```

---

## 第五步：帮助文档更新

更新 `docs/akshare_help_summary.md`，新增以下章节：
- "浏览器伪装与反爬策略" 使用说明
- "Cookie/Session 注入" 使用指南
- "断点续传" 使用指南
- "进度回调" 使用指南
- "限频配置" 使用指南

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `akshare/utils/context.py` | 修改 | 扩展 AkshareConfig，新增 API 函数 |
| `akshare/utils/session.py` | 新增 | BrowserSessionManager |
| `akshare/utils/request.py` | 修改 | 增强 request_with_retry |
| `akshare/request.py` | 修改 | 增强 make_request_with_retry |
| `akshare/__init__.py` | 修改 | 导出新 API |
| `akshare/exceptions.py` | 修改 | 新增 CheckpointError |
| `services/akshare_pro.py` | 修改 | 重构为使用核心 API |
| `services/qlib_instruments_updater.py` | 修改 | 适配新接口 |
| `tests/test_session_manager.py` | 新增 | 单元测试 |
| `docs/akshare_help_summary.md` | 修改 | 更新帮助文档 |
