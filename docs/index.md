---
home: true
icon: home
title: 首页
heroImage: https://akshare.akfamily.xyz/_static/akshare_logo.jpg
heroText: AKShare Pro
tagline: 开源财经数据接口库 · 增强版 — 浏览器伪装 / Cookie 注入 / 智能限频 / 断点续传
actions:
  - text: 快速开始
    icon: lightbulb
    link: /introduction.md
    type: primary

  - text: 数据接口
    icon: database
    link: /data/stock/stock.md

  - text: 反爬增强指南
    icon: shield-halved
    link: /akshare_help_summary.md#_18-浏览器伪装与反爬增强-aksharepro-扩展
    type: secondary

highlights:
  - header: 500+ 金融数据接口
    description: 覆盖股票、期货、期权、基金、外汇、债券、宏观等全品种数据
    features:
      - title: A 股实时/历史行情
        icon: chart-line
        details: 东方财富、新浪、雪球等多数据源，支持复权、分钟线
      - title: 期货 & 期权数据
        icon: industry
        details: 主力合约、持仓排名、仓单、期权龙虎榜
      - title: 基金 & 债券
        icon: piggy-bank
        details: 公募/私募基金净值、可转债、国债收益率
      - title: 宏观经济数据
        icon: earth-americas
        details: 中国/美国/欧洲/日本等 CPI、GDP、PMI 指标

  - header: Pro 增强能力
    description: 所有接口自动获得反爬伪装能力，零代码修改
    features:
      - title: 浏览器级伪装
        icon: user-secret
        details: Per-host 请求头模板，模拟 Chrome/Edge 最新浏览器指纹
      - title: Cookie / Session 注入
        icon: cookie-bite
        details: ak.set_cookies() 注入浏览器登录态，支持 per-host 粒度
      - title: 智能限频
        icon: gauge-high
        details: 东财 1.5-3s、新浪 0.5-1.5s，per-host 独立策略
      - title: 断点续传
        icon: rotate
        details: ak.set_checkpoint() 启用，中断后自动从断点恢复
      - title: 进度回调
        icon: spinner
        details: ak.set_progress_callback() 实时感知数据获取进度
      - title: 向后兼容
        icon: check-double
        details: 所有新参数有默认值，500+ 接口零修改即用
---
