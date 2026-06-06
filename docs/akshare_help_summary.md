# AKShare 帮助文档总结

> 来源：https://akshare.akfamily.xyz/
> 整理时间：2026-06-06
> 文档更新时间：2026-05-27

---

## 1. 项目概览

AKShare 是基于 Python 的开源财经数据接口库，涵盖股票、期货、期权、基金、外汇、债券、指数、加密货币等金融产品的数据采集、清洗与落地，主要用于学术研究。

- 所有数据来自**公开数据源**，不涉及隐私
- 代码符合 PEP8 规范，最佳支持 Python 3.12+
- 提供 HTTP API 工具 [AKTools](https://aktools.akfamily.xyz/) 支持非 Python 用户
- 引用格式：`@misc{akshare2022, author={Albert King}, ...}`

---

## 2. 安装指导

### 系统要求
- 仅支持 **64 位**操作系统
- Python **3.9+**（推荐 3.11.x）
- 推荐安装最新版 Anaconda

### 安装命令

```bash
# 通用安装
pip install akshare --upgrade

# 国内安装（Python）
pip install akshare --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple

# 国内安装（Anaconda）
pip install akshare --upgrade --user -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**注意**：程序文件名/文件夹名不能是 `akshare`

### 跨平台支持
- **M 系列芯片**：已默认适配，直接 pip install 即可
- **树莓派 4B**：安装 Raspberry Pi OS 64-bit，创建虚拟环境后安装
- **R 语言**：通过 `reticulate` 包调用 AKShare（推荐用 AKTools HTTP API）
- **MATLAB**：通过 `py.akshare.xxx` 方式调用（推荐用 AKTools HTTP API）

### 常见安装报错
1. **安装超时**：`pip --default-timeout=100 install -U akshare` 或使用代理
2. **拒绝访问**：使用 `--user` 参数或管理员权限
3. **其他错误**：确认 Python 3.9+ 64 位，或使用 conda 虚拟环境

---

## 3. 环境配置（Anaconda）

### 安装步骤
1. 从[清华大学镜像站](https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/)下载安装 Anaconda（64 位）
2. 安装时勾选"Add to PATH"选项
3. 创建虚拟环境：`conda create -n ak_test python=3.9`
4. 激活环境：`conda activate ak_test`
5. 安装 AKShare：`pip install akshare --upgrade`
6. 验证安装：`import akshare as ak; print(ak.__version__)`

---

## 4. 快速入门

AKShare 提供丰富的数据接口，覆盖以下主要数据类别：

| 数据类别 | 示例接口 | 说明 |
|---------|---------|------|
| 交易所期货 | `get_cffex_daily` | 中金所、郑商所、大商所、上期所等 |
| 期权数据 | `option_hist_dce` | 商品期权、金融期权 |
| 债券数据 | `bond_zh_hs_daily` | 沪深债券、可转债 |
| 外汇数据 | `get_fx_spot_quote` | 人民币外汇即期/远掉报价 |
| 宏观经济 | `macro_china_gdp_yearly` | 中国/美国/欧洲等宏观数据 |
| A 股行情 | `stock_zh_a_hist` | 实时行情、历史 K 线、分时数据 |
| 港股/美股 | `stock_hk_spot_em` | 港股、美股行情与历史数据 |
| 基金数据 | `fund_name_em` | 基金信息、净值、排行、持仓 |
| 指数数据 | `stock_zh_index_daily` | 股票指数、申万指数、财新指数 |
| 资金流向 | `stock_individual_fund_flow` | 个股/板块/概念资金流 |
| 财务数据 | `stock_financial_abstract` | 三大报表、财务指标 |
| 加密货币 | `crypto_js_spot` | 主流加密货币行情 |

### 使用示例

```python
import akshare as ak

# 获取 A 股日频数据
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date="20210907", adjust="")

# 获取期货展期收益率
df = ak.get_roll_yield_bar(type_method="date", var="RB", start_day="20180618", end_day="20180718")
```

---

## 5. 指标计算

### 已实现波动率（Yang-Zhang）

- 接口：`volatility_yz_rv`
- 输入：包含日期和 OHLC 价格的 DataFrame
- 输出：日频率的已实现波动率数据（date, rv）

```python
stock_df = ak.rv_from_stock_zh_a_hist_min_em(symbol="000001", period="5")
rv_df = ak.volatility_yz_rv(data=stock_df)
```

---

## 6. 数据说明

部分数据接口存在已知问题需注意：

- `stock_zh_a_hist`：某些股票后复权数据（如 600734）可能出现开高低收负值，这是数据源本身的问题
- 使用前建议先检查数据质量

---

## 7. 实盘交易

### 证券实盘
- 提供股票、期权、两融等账户的实盘 API 接口对接
- 支持 QMT/PTRADE/聚宽等量化软件
- 提供策略编写、指标定制、量化工具定制等服务

### 期货实盘
- 提供量化咨询、软件指导、策略编写、外接托管等服务
- 通过专用网络/系统/席位/服务器托管保障高效稳定交易

---

## 8. 答疑专栏（常见问题 FAQ）

| 问题 | 解决方案 |
|------|---------|
| 安装速度慢 | 使用国内源：`pip install akshare -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com --upgrade` |
| `module 'akshare' has no attribute 'xxx'` | 检查 Python 3.9+；升级到最新版；检查接口是否存在；文件名不能叫 `akshare.py` |
| 无法获取指定日期期间数据 | 部分接口无 `start_date/end_date` 参数，调用后自行过滤 |
| `ReadTimeout` 超时 | 重新运行；更换 IP/使用代理；降低访问频率 |
| `cannot import 'StringIO'` | 升级 pandas：`pip install pandas --upgrade` |
| 数据返回错位 | 多次重试；切换 IP；到 GitHub Issues 反馈 |
| Linux `JavaScript runtime` 错误 | 安装 `nodejs` |
| 数据在 IDE 中显示不全 | 设置 `pd.set_option('display.max_columns', None)` 等 |
| `MiniRacer has no attribute 'ext'` | 安装 64 位 Python |
| 代理报错 `check_hostname` | `pip install urllib3==1.25.8` |

---

## 9. 量化专题

### 开源量化平台
- **AKQuant**（强烈推荐）：https://github.com/akfamily/akquant
- **PyBroker**：https://www.pybroker.com/
- **Backtrader**：https://www.backtrader.com/
- **VN.PY**：https://www.vnpy.com/
- **功夫量化**：https://www.kungfu-trader.com/

### 网页端量化平台
BigQuant、JoinQuant、MyQuant、Uqer、RiceQuant、WindQuant

### 常见量化策略类型
双均线、alpha对冲、集合竞价选股、多因子选股、网格交易、指数增强、跨品种套利、跨期套利、日内回转交易、做市商交易、海龟交易法、行业轮动、机器学习

---

## 10. 策略示例

### AKQuant（强烈推荐）
高性能量化投研框架，支持安装：`pip install akquant`

### PyBroker
基于机器学习的量化回测框架，安装：`pip install libpybroker`

### Backtrader
经典回测框架，安装：`pip install backtrader`

```python
# Backtrader 示例
import backtrader as bt
import akshare as ak

cerebro = bt.Cerebro()
stock_df = ak.stock_zh_a_daily(symbol="sz000001", adjust="qfq")
data = bt.feeds.PandasData(dataname=stock_df)
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.run()
```

---

## 11. 贡献源码指南

### 代码规范
- 符合 **PEP 8**，使用 [Ruff](https://github.com/astral-sh/ruff) 格式化
- 使用 [pre-commit](https://pre-commit.com/) 规范提交
- 接口命名格式：`stock_zh_a_hist_sina`（金融产品_国家/地区_市场/品种_数据类型_数据源）
- 所有返回格式统一为 `pandas.DataFrame`

### 文档规范
- 新增/修改接口后需同步更新文档
- 文档包含：接口名、目标地址、描述、限量、输入/输出参数、接口示例、数据示例
- 输出字段类型限于：`int64`、`float64`、`object`

### 提交流程
- 从 `dev` 分支克隆
- 提交到 `dev` 分支

---

## 12. 依赖说明

| 依赖库 | 版本要求 | 说明 |
|--------|---------|------|
| mini-racer | >=0.12.4 | JavaScript 运行时（替代已停止维护的 PyExecJS） |
| pandas | >=0.25.0（推荐最新） | 数据清洗核心库，默认安装 NumPy |

---

## 13. HTTP 部署（AKTools）

```bash
# 安装
pip install aktools

# 运行
python -m aktools
```

- 体验版：`pip install aktools==0.0.68`
- 完整版支持认证、权限、可视化页面
- 详情：https://aktools.akfamily.xyz/

---

## 14. Docker 部署

```bash
# 拉取镜像
docker pull registry.cn-shanghai.aliyuncs.com/akfamily/aktools:jupyter

# 运行容器
docker run -it registry.cn-shanghai.aliyuncs.com/akfamily/aktools:jupyter

# 带 JupyterLab 运行
docker run -it -p 8888:8888 --name akdocker -v /c/home:/home registry.cn-shanghai.aliyuncs.com/akfamily/aktools:jupyter jupyter-lab --allow-root --no-browser --ip=0.0.0.0
```

- 镜像在每次 AKShare 更新时自动更新
- 容器内可通过 `!pip install akshare --upgrade` 升级

---

## 15. 特别说明

### 致谢数据源
东方财富、新浪财经、生意社、奇货可查、中国银行间市场交易商协会、99 期货、中国外汇交易中心、金十数据、和讯财经、上海证券交易所、深证证券交易所、各期货交易所等 30+ 公开数据源。

### 免责声明
1. 数据接口和数据**仅用于学术研究**，不可做商业用途
2. 数据仅供参考，**不构成投资建议**
3. 未来可能因不可抗拒之力移除部分数据接口

---

## 16. 相关文章与资源

### 公众号文章
- 用 Python 快速获取基金股票持仓增减情况
- AkShare 之 ETF 历史行情
- 零基础量化交易学习 Pandas
- 时间序列平稳性检验方法汇总

### 博客文章
- akshare 做 MFI 策略 / SMA 策略 / 布林通道策略 / 配对策略
- 用 AkShare 获取 A 股数据、分钟 K 线、可转债数据
- 股债收益模型量化实战

---

## 17. 数据字典（数据分类索引）

AKShare 数据字典按以下类别组织，每个类别下包含多个具体接口：

| 类别 | 主要内容 |
|------|---------|
| 股票数据 | A 股/港股/美股行情、财务数据、股东信息、龙虎榜、融资融券等 |
| 期货数据 | 交易所行情、持仓排名、仓单、库存、交割、手续费等 |
| 债券数据 | 沪深债券、可转债、国债收益率、中债指数等 |
| 期权数据 | 金融期权、商品期权、期权龙虎榜、波动率指数等 |
| 外汇数据 | 汇率行情、外汇掉期、外币对报价等 |
| 基金数据 | 公募/私募基金、ETF、LOF、基金评级、基金经理等 |
| 宏观数据 | 中国/美国/欧洲/日本等宏观经济指标 |
| 指数数据 | 股票指数、申万指数、财新指数、中证指数等 |
| 另类数据 | 电影票房、空气质量、迁徙数据、加密货币等 |
| 工具箱 | 交易日历、货币换算、NLP 等 |

---

## 18. 浏览器伪装与反爬增强（aksharepro 扩展）

> aksharepro 在核心库基础上增强了反爬伪装能力，所有 500+ 接口自动受益，无需修改调用代码。

### 18.1 架构概述

```
用户代码
    ↓
akshare.xxx()  (500+ 接口，无需修改)
    ↓
akshare/utils/request.py  request_with_retry()  ← 改造核心
    ↓
akshare/utils/context.py  AkshareConfig  ← 扩展配置
    ↓
BrowserSessionManager  ← 浏览器会话管理器
    ├── 浏览器级请求头（per-host）
    ├── Cookie/Session 注入
    ├── 进度回调
    ├── 断点续传
    └── 智能限频
```

### 18.2 Cookie 注入

用户在浏览器登录后，将 Cookie 导出并注入到 AKShare：

```python
import akshare as ak

# 全局 Cookie（所有站点生效）
ak.set_cookies({"token": "abc123"})

# per-host Cookie（仅指定站点生效）
ak.set_cookies({"xq_a_token": "xxx"}, host="xueqiu.com")

# 字符串格式
ak.set_cookies("key1=val1; key2=val2", host="eastmoney.com")

# 然后正常使用，请求中自动包含 Cookie
df = ak.stock_zh_a_hist(symbol="000001", period="daily")
```

**上下文管理器方式（临时生效）**：

```python
with ak.CookieContext({"xq_a_token": "xxx"}, host="xueqiu.com"):
    df = ak.stock_xq(...)
# 退出后自动清除
```

### 18.3 自定义 Session

高级用法，允许传入自定义 `requests.Session`：

```python
import requests
import akshare as ak

s = requests.Session()
s.headers.update({"Authorization": "Bearer xxx"})
ak.set_session(s)

# 后续所有请求使用该 Session
df = ak.stock_zh_a_spot_em()
```

### 18.4 进度回调

```python
import akshare as ak

def on_progress(pct: int, msg: str):
    print(f"[{pct}%] {msg}")

ak.set_progress_callback(on_progress)

# 数据获取过程中自动触发回调
df = ak.stock_zh_a_spot_em()
```

### 18.5 智能限频

每个站点独立的请求频率控制，避免触发反爬：

```python
import akshare as ak

# 东财请求间隔 1.5~3 秒
ak.set_rate_limit("eastmoney.com", min_delay=1.5, max_delay=3.0)

# 雪球请求间隔 0.8~2 秒
ak.set_rate_limit("xueqiu.com", min_delay=0.8, max_delay=2.0)
```

**默认限频策略**：

| 站点 | 最小延迟 | 最大延迟 |
|------|---------|----------|
| eastmoney.com | 1.5s | 3.0s |
| sina.com.cn | 0.5s | 1.5s |
| xueqiu.com | 0.8s | 2.0s |
| 其他站点 | 0.3s | 1.0s |

### 18.6 断点续传

支持分页数据获取中断后从断点继续：

```python
import akshare as ak

# 启用断点续传
ak.set_checkpoint(True, directory="./my_checkpoints")

# 数据获取（中断后重新运行会自动恢复）
df = ak.stock_zh_a_spot_em()
```

### 18.7 Per-host 浏览器请求头

自动根据请求 URL 匹配对应站点的浏览器级请求头：

| 站点 | User-Agent | Referer | 特殊处理 |
|------|-----------|---------|----------|
| eastmoney.com | Chrome/Edge | quote.eastmoney.com | Origin 头 |
| sina.com.cn | Chrome/Edge | finance.sina.com.cn | 禁用压缩(GBK) |
| xueqiu.com | Chrome/Edge | xueqiu.com | - |
| qq.com | Chrome/Edge | web.sqt.gtimg.cn | - |
| 10jqka.com.cn | Chrome/Edge | data.10jqka.com.cn | - |
| cninfo.com.cn | Chrome/Edge | webapi.cninfo.com.cn | - |

### 18.8 AKSharePro 包装器

`AKSharePro` 提供一站式配置入口：

```python
from services.akshare_pro import AKSharePro

# 基础用法
akp = AKSharePro()
df = akp.stock_zh_a_spot_em()

# 完整配置
akp = AKSharePro(
    cookies={"xq_a_token": "xxx"},
    cookie_host="xueqiu.com",
    progress_callback=lambda pct, msg: print(f"[{pct}%] {msg}"),
    rate_limits={"eastmoney.com": (1.5, 3.0)},
    checkpoint_enabled=True,
    checkpoint_dir="./checkpoints",
)
```

### 18.9 API 参考

| 函数 | 说明 |
|------|------|
| `ak.set_cookies(cookies, host=None)` | 设置 Cookie（全局或 per-host） |
| `ak.get_cookies(host=None)` | 获取 Cookie |
| `ak.clear_cookies(host=None)` | 清除 Cookie |
| `ak.set_session(session)` | 设置自定义 Session |
| `ak.get_session()` | 获取自定义 Session |
| `ak.set_progress_callback(callback)` | 设置进度回调 |
| `ak.get_progress_callback()` | 获取进度回调 |
| `ak.set_rate_limit(host, min_delay, max_delay)` | 设置 per-host 限频 |
| `ak.set_checkpoint(enabled, directory)` | 配置断点续传 |
| `ak.CookieContext(cookies, host)` | Cookie 上下文管理器 |
| `ak.SessionContext(session)` | Session 上下文管理器 |
| `ak.ProxyContext(proxies)` | 代理上下文管理器 |

### 18.10 向后兼容性

所有新增参数均有默认值，现有 500+ 接口无需任何修改即可工作：
- 默认启用浏览器级请求头伪装
- 默认启用 per-host 智能限频
- 默认 Session 连接池复用
- Cookie / 进度回调 / 断点续传均为可选功能
