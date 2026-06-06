# AKShare Pro — 增强版开源财经数据接口库

> 基于 [AKShare](https://github.com/akfamily/akshare)，新增 **浏览器级反爬伪装**、**Cookie/Session 注入**、**智能限频**、**断点续传** 等企业级能力。

**资源分享**：对于想了解更多财经数据与量化投研的小伙伴，推荐一个专注于财经数据和量化研究的知识社区。
该社区提供相关文档和视频学习资源，汇集了各类财经数据源和量化投研工具的使用经验。
有兴趣深入学习的朋友可点此[了解更多](https://t.zsxq.com/ZCxUG)，也推荐大家关注微信公众号【数据科学实战】。

**重磅推荐**：AKQuant 是一款专为 **量化投研 (Quantitative Research)** 打造的高性能量化回测框架。它以 Rust 铸造极速撮合内核，
以 Python 链接数据与 AI 生态，旨在为量化投资者提供可靠高效的量化投研解决方案。参见[AKQuant](https://github.com/akfamily/akquant)

**工具推荐**：期魔方是一款本地化期货量化分析工具，适合数据分析爱好者使用。无需复杂部署，支持数据分析和机器学习功能，研究功能免费开放。
如需了解更多信息可访问[期魔方](https://qmfquant.com)。

![AKShare Logo](https://github.com/akfamily/akshare/blob/main/assets/images/akshare_logo.jpg)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/akshare.svg)](https://pypi.org/project/akshare/)
[![PyPI](https://img.shields.io/pypi/v/akshare.svg)](https://pypi.org/project/akshare/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/akshare?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/akshare)
[![Documentation Status](https://readthedocs.org/projects/akshare/badge/?version=latest)](https://akshare.readthedocs.io/?badge=latest)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![akshare](https://img.shields.io/badge/Data%20Science-AKShare-green)](https://github.com/akfamily/akshare)
[![Actions Status](https://github.com/akfamily/akshare/actions/workflows/release_and_deploy.yml/badge.svg)](https://github.com/akfamily/akshare/actions)
[![MIT Licence](https://img.shields.io/badge/license-MIT-blue)](https://github.com/akfamily/akshare/blob/main/LICENSE)
[![](https://img.shields.io/github/forks/jindaxiang/akshare)](https://github.com/akfamily/akshare)
[![](https://img.shields.io/github/stars/jindaxiang/akshare)](https://github.com/akfamily/akshare)
[![](https://img.shields.io/github/issues/jindaxiang/akshare)](https://github.com/akfamily/akshare)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)

---

## ✨ Pro 增强特性

AKShare Pro 在核心库基础上进行了深度架构改造，**所有 500+ 接口自动受益，零代码修改**：

| 特性 | 说明 |
|------|------|
| 🛡️ **浏览器级伪装** | Per-host 请求头模板，模拟 Chrome/Edge 最新浏览器指纹，覆盖东财、新浪、雪球、腾讯、同花顺等站点 |
| 🍪 **Cookie/Session 注入** | `ak.set_cookies()` 注入浏览器登录态 Cookie，支持全局或 per-host 粒度 |
| ⚡ **智能限频** | Per-host 独立限频策略（东财 1.5-3s、新浪 0.5-1.5s…），有效避免封 IP |
| 🔄 **断点续传** | `ak.set_checkpoint()` 启用，分页数据获取中断后自动从断点恢复 |
| 📊 **进度回调** | `ak.set_progress_callback()` 实时感知数据获取进度 |
| 🔌 **向后兼容** | 所有新参数有默认值，现有 500+ 接口无需任何修改 |

### 快速上手

```python
import akshare as ak

# 1. 注入浏览器 Cookie（在浏览器登录后导出）
ak.set_cookies({"xq_a_token": "xxx"}, host="xueqiu.com")

# 2. 设置进度回调
def on_progress(pct: int, msg: str):
    print(f"[{pct}%] {msg}")
ak.set_progress_callback(on_progress)

# 3. 启用断点续传
ak.set_checkpoint(True, directory="./checkpoints")

# 4. 正常使用 —— 所有接口自动获得反爬伪装
df = ak.stock_zh_a_hist(symbol="000001", period="daily")
```

### 架构概览

```
用户代码
    ↓
akshare.xxx()  (500+ 接口，无需修改)
    ↓
request_with_retry()  ← 改造核心
    ↓
BrowserSessionManager  ← 浏览器会话管理器
    ├── 浏览器级请求头（per-host）
    ├── Cookie / Session 注入
    ├── 智能限频
    ├── 断点续传
    └── 进度回调
```

详细文档请参阅 [反爬增强指南](docs/akshare_help_summary.md#_18-浏览器伪装与反爬增强-aksharepro-扩展)。

---

## 概览 / Overview

[AKShare](https://github.com/akfamily/akshare) 需要 Python(64位) 3.9 及以上版本，旨在简化财经数据获取流程。

**一行代码，数据到手！**

- 文档：[中文文档](https://delon-xie.github.io/aksharepro/)

## 安装 / Installation

### 通用安装 / General

```shell
pip install aksharepro --upgrade
```

### 国内加速 / China

```shell
pip install aksharepro -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com --upgrade
```

### Docker

```shell
docker pull registry.cn-shanghai.aliyuncs.com/akfamily/aktools:jupyter
docker run -it registry.cn-shanghai.aliyuncs.com/akfamily/aktools:jupyter python
```

## 使用示例 / Usage

### 数据获取 / Data

```python
import akshare as ak

stock_zh_a_hist_df = ak.stock_zh_a_hist(
    symbol="000001", period="daily",
    start_date="20170301", end_date="20231022", adjust=""
)
print(stock_zh_a_hist_df)
```

```
      日期          开盘   收盘    最高  ...  振幅   涨跌幅  涨跌额  换手率
0     2017-03-01   9.49   9.49   9.55  ...  0.84  0.11  0.01  0.21
1     2017-03-02   9.51   9.43   9.54  ...  1.26 -0.63 -0.06  0.24
2     2017-03-03   9.41   9.40   9.43  ...  0.74 -0.32 -0.03  0.20
3     2017-03-06   9.40   9.45   9.46  ...  0.74  0.53  0.05  0.24
4     2017-03-07   9.44   9.45   9.46  ...  0.63  0.00  0.00  0.17
          ...    ...    ...    ...  ...   ...   ...   ...   ...
1610  2023-10-16  11.00  11.01  11.03  ...  0.73  0.09  0.01  0.26
1611  2023-10-17  11.01  11.02  11.05  ...  0.82  0.09  0.01  0.25
1612  2023-10-18  10.99  10.95  11.02  ...  1.00 -0.64 -0.07  0.34
1613  2023-10-19  10.91  10.60  10.92  ...  3.01 -3.20 -0.35  0.61
1614  2023-10-20  10.55  10.60  10.67  ...  1.51  0.00  0.00  0.27
[1615 rows x 11 columns]
```

### K 线绘图 / Plot

```python
import akshare as ak
import mplfinance as mpf  # pip install mplfinance

stock_us_daily_df = ak.stock_us_daily(symbol="AAPL", adjust="qfq")
stock_us_daily_df = stock_us_daily_df.set_index(["date"])
stock_us_daily_df = stock_us_daily_df["2020-04-01": "2020-04-29"]
mpf.plot(stock_us_daily_df, type="candle", mav=(3, 6, 9), volume=True, show_nontrading=False)
```

![KLine](https://jfds-1252952517.cos.ap-chengdu.myqcloud.com/akshare/readme/home/AAPL_candle.png)

---

## 🛡️ Pro 增强功能详解 / Pro Enhanced Features

### 浏览器级反爬伪装 / Browser-Level Anti-Crawling

自动根据请求 URL 匹配 Per-host 浏览器请求头（User-Agent、Referer、Origin 等），模拟 Chrome/Edge 最新版本：

```python
# 无需配置，自动生效
df = ak.stock_zh_a_spot_em()  # 东财 → 自动注入东财专属请求头
```

**支持的站点**：东方财富、新浪财经、雪球、腾讯财经、同花顺、巨潮资讯、中国外汇交易中心、上交所、深交所等。

### Cookie / Session 注入 / Cookie & Session Injection

用户在浏览器登录后，将 Cookie 导出并注入 AKShare：

```python
import akshare as ak

# 全局 Cookie
ak.set_cookies({"token": "abc123"})

# Per-host Cookie（仅指定站点生效）
ak.set_cookies({"xq_a_token": "xxx"}, host="xueqiu.com")

# 自定义 Session
import requests
s = requests.Session()
s.headers.update({"Authorization": "Bearer xxx"})
ak.set_session(s)

# 上下文管理器（临时生效）
with ak.CookieContext({"xq_a_token": "xxx"}, host="xueqiu.com"):
    df = ak.stock_xq(...)
```

### 智能限频 / Smart Rate Limiting

每个站点独立的请求频率控制，有效避免触发反爬封禁：

```python
import akshare as ak

# 自定义限频
ak.set_rate_limit("eastmoney.com", min_delay=1.5, max_delay=3.0)
ak.set_rate_limit("xueqiu.com", min_delay=0.8, max_delay=2.0)
```

| 站点 / Site | 默认最小延迟 | 默认最大延迟 |
|-------------|------------|------------|
| eastmoney.com | 1.5s | 3.0s |
| sina.com.cn | 0.5s | 1.5s |
| xueqiu.com | 0.8s | 2.0s |
| 其他 / Others | 0.3s | 1.0s |

### 断点续传 / Checkpoint & Resume

分页数据获取中断后，再次运行自动从断点恢复：

```python
import akshare as ak

ak.set_checkpoint(True, directory="./my_checkpoints")
df = ak.stock_zh_a_spot_em()  # 中断后重新运行，自动恢复进度
```

### 进度回调 / Progress Callback

```python
import akshare as ak

def on_progress(pct: int, msg: str):
    print(f"[{pct}%] {msg}")

ak.set_progress_callback(on_progress)
df = ak.stock_zh_a_spot_em()
# 输出示例:
# [10%] 第一页完成，共 53 页
# [25%] 已获取第 8/53 页，共 800 条
# ...
```

---

## 特性 / Features

- **简单易用 / Easy of use**：一行代码获取数据；
- **可扩展 / Extensible**：易于与其他应用集成定制；
- **强大 / Powerful**：依托 Python 生态；
- **反爬增强 / Anti-Crawling Enhanced**：浏览器级伪装 + 智能限频 + Cookie 注入；
- **断点续传 / Checkpoint Resume**：大数据量分页获取中断后可恢复；
- **向后兼容 / Backward Compatible**：500+ 接口零修改即用。

## 教程 / Tutorials

1. [项目概览 / Overview](https://delon-xie.github.io/aksharepro/introduction.html)
2. [安装指导 / Installation](https://delon-xie.github.io/aksharepro/installation.html)
3. [使用教程 / Tutorial](https://delon-xie.github.io/aksharepro/tutorial.html)
4. [数据字典 / Data Dict](https://delon-xie.github.io/aksharepro/data/index.html)
5. [专题教程 / Subjects](https://delon-xie.github.io/aksharepro/topic/index.html)

## 贡献 / Contribution

[AKShare](https://github.com/akfamily/akshare) 仍在持续开发中，欢迎提交 Issue 和 Pull Request：

- 报告或修复 Bug
- 请求或新增数据接口
- 编写或修正文档
- 添加测试用例

> Notice: We use [Ruff](https://github.com/astral-sh/ruff) to format the code

## 声明 / Statement

1. [AKShare](https://github.com/akfamily/akshare) 提供的所有数据仅供学术研究和数据分析使用；
2. [AKShare](https://github.com/akfamily/akshare) 提供的数据仅供参考，不构成任何投资建议；
3. 基于 [AKShare](https://github.com/akfamily/akshare) 进行研究的投资者应关注数据风险；
4. [AKShare](https://github.com/akfamily/akshare) 将持续坚持开源财经数据；
5. 基于不可控因素，部分数据接口可能被移除；
6. 请遵循 [AKShare](https://github.com/akfamily/akshare) 使用的相关开源协议；
7. 为非 Python 用户提供 HTTP API：[AKTools](https://aktools.readthedocs.io/)。

## 徽章 / Badge

在您的项目 README 中使用徽章：

```markdown
[![Data: akshare](https://img.shields.io/badge/Data%20Science-AKShare-green)](https://github.com/akfamily/akshare)
```

[![Data: akshare](https://img.shields.io/badge/Data%20Science-AKShare-green)](https://github.com/akfamily/akshare)

## 引用 / Citation

```bibtex
@misc{akshare,
    author = {Albert King and Yaojie Zhang},
    title = {AKShare},
    year = {2022},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/akfamily/akshare}},
}
```

## 致谢 / Acknowledgement

Special thanks [FuShare](https://github.com/LowinLi/fushare) for the opportunity of learning from the project;

Special thanks [TuShare](https://github.com/waditu/tushare) for the opportunity of learning from the project;

Thanks for the data provided by [东方财富网站](http://data.eastmoney.com);

Thanks for the data provided by [新浪财经网站](https://finance.sina.com.cn);

Thanks for the data provided by [金十数据网站](https://www.jin10.com/);

Thanks for the data provided by [生意社网站](http://www.100ppi.com/);

Thanks for the data provided by [中国银行间市场交易商协会网站](http://www.nafmii.org.cn/);

Thanks for the data provided by [99期货网站](http://www.99qh.com/);

Thanks for the data provided by [中国外汇交易中心暨全国银行间同业拆借中心网站](http://www.chinamoney.com.cn/chinese/);

Thanks for the data provided by [和讯财经网站](http://www.hexun.com/);

Thanks for the data provided by [DACHENG-XIU 网站](https://dachxiu.chicagobooth.edu/);

Thanks for the data provided by [上海证券交易所网站](http://www.sse.com.cn/assortment/options/price/);

Thanks for the data provided by [深证证券交易所网站](http://www.szse.cn/);

Thanks for the data provided by [北京证券交易所网站](http://www.bse.cn/);

Thanks for the data provided by [中国金融期货交易所网站](http://www.cffex.com.cn/);

Thanks for the data provided by [上海期货交易所网站](http://www.shfe.com.cn/);

Thanks for the data provided by [大连商品交易所网站](http://www.dce.com.cn/);

Thanks for the data provided by [郑州商品交易所网站](http://www.czce.com.cn/);

Thanks for the data provided by [上海国际能源交易中心网站](http://www.ine.com.cn/);

Thanks for the data provided by [Timeanddate 网站](https://www.timeanddate.com/);

Thanks for the data provided by [河北省空气质量预报信息发布系统网站](http://110.249.223.67/publish/);

Thanks for the data provided by [Economic Policy Uncertainty 网站](http://www.nanhua.net/nhzc/varietytrend.html);

Thanks for the data provided by [申万指数网站](http://www.swsindex.com/idx0120.aspx?columnid=8832);

Thanks for the data provided by [真气网网站](https://www.zq12369.com/);

Thanks for the data provided by [财富网站](http://www.fortunechina.com/);

Thanks for the data provided by [中国证券投资基金业协会网站](http://gs.amac.org.cn/);

Thanks for the data provided by [Expatistan 网站](https://www.expatistan.com/cost-of-living);

Thanks for the data provided by [北京市碳排放权电子交易平台网站](https://www.bjets.com.cn/article/jyxx/);

Thanks for the data provided by [国家金融与发展实验室网站](http://www.nifd.cn/);

Thanks for the data provided by [义乌小商品指数网站](http://www.ywindex.com/Home/Product/index/);

Thanks for the data provided by [百度迁徙网站](https://qianxi.baidu.com/?from=shoubai#city=0);

Thanks for the data provided by [思知网站](https://www.ownthink.com/);

Thanks for the data provided by [Currencyscoop 网站](https://currencyscoop.com/);

Thanks for the data provided by [新加坡交易所网站](https://www.sgx.com/zh-hans/research-education/derivatives).
