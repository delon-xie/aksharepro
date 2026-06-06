# AKShare 项目概览（帮助文件总结）

> 来源：https://delon-xie.github.io/aksharepro/introduction.html
> 文档更新时间：2026-05-27

## 项目简介

AKShare 是基于 Python 的开源财经数据接口库，旨在实现对股票、期货、期权、基金、外汇、债券、指数、加密货币等金融产品的：

- **基本面数据**采集
- **实时与历史行情数据**采集
- **衍生数据**加工与落地

涵盖从数据采集、数据清洗到数据落地的完整流程，主要用于学术研究目的。

## 核心特色

1. 代码语法符合 PEP8 规范，数据接口命名统一
2. 最佳支持 Python 3.12 及以上版本
3. 每个数据接口均提供详细说明和示例，复制粘贴即可下载数据
4. 持续维护因目标网页变化导致的接口异常问题
5. 持续更新财经数据接口并优化源代码
6. 提供完善的接口文档，提高易用性
7. 为非 Python 用户提供 HTTP API 接口工具 [AKTools](https://aktools.akfamily.xyz/)

## 数据特点

- 所有数据均来自**公开数据源**，不涉及个人隐私数据和非公开数据
- 获取相对权威的财经数据网站原始数据
- 通过多数据源交叉验证进行再加工，得出科学结论
- 后续将基于学术论文和研究报告添加更多数据接口和衍生指标

## 使用注意事项

- 数据接口及相关数据**仅用于学术研究**
- 个人、机构及团体使用请注意**商业风险**
- 由于目标网站格式变化，需要**经常更新**到最新版本
- 关注项目文档更新，了解最新使用方式和接口变更

## HTTP API 版本

项目提供 [AKTools](https://github.com/akfamily/aktools) 作为 AKShare 的 HTTP API 版本，突破 Python 语言限制，适用于非 Python 用户。

## 引用格式

```bibtex
@misc{akshare2022,
    author = {Albert King},
    title = {AKShare},
    year = {2022},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/akfamily/akshare}},
}
```

## 问题反馈

如有 AKShare 库、文档及数据的相关问题，请在 [AKShare Issues](https://github.com/akfamily/akshare/issues) 中提 Issues。

## 致谢

特别感谢 [FuShare](https://github.com/LowinLi/fushare) 和 [TuShare](https://github.com/waditu/tushare) 在代码和项目开发上提供的借鉴和学习机会。
