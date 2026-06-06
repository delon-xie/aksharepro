import { defineUserConfig } from "vuepress";
import { viteBundler } from "@vuepress/bundler-vite";
import { hopeTheme } from "vuepress-theme-hope";

export default defineUserConfig({
  // 站点配置
  lang: "zh-CN",
  title: "AKShare Pro",
  description: "AKShare 增强版 —— 浏览器伪装、Cookie 注入、智能限频、断点续传",

  // GitHub Pages 部署时需要设置 base 为仓库名
  base: "/aksharepro/",

  // 主题配置
  theme: hopeTheme({
    // 基本配置
    hostname: "https://delon-xie.github.io/aksharepro/",
    author: {
      name: "AKShare Pro",
      url: "https://github.com/delon-xie/aksharepro",
    },
    logo: "https://delon-xie.github.io/aksharepro/assets/images/akshare_logo.jpg",
    repo: "delon-xie/aksharepro",
    docsDir: "docs",

    // 导航栏
    navbar: [
      "/",
      {
        text: "快速开始",
        icon: "rocket",
        prefix: "/",
        children: [
          "introduction.md",
          "installation.md",
          "anaconda.md",
          "tutorial.md",
          "demo.md",
        ],
      },
      {
        text: "数据接口",
        icon: "database",
        prefix: "/data/",
        children: [
          "stock/stock.md",
          "futures/futures.md",
          "bond/bond.md",
          "fund/fund_public.md",
          "fund/fund_private.md",
          "option/option.md",
          "fx/fx.md",
          "macro/macro.md",
          "index/index.md",
          "currency/currency.md",
          "energy/energy.md",
        ],
      },
      {
        text: "反爬增强",
        icon: "shield-halved",
        link: "/akshare_help_summary.md#_18-浏览器伪装与反爬增强-aksharepro-扩展",
      },
      {
        text: "更多",
        icon: "ellipsis",
        prefix: "/",
        children: [
          "contributing.md",
          "changelog.md",
          "articles.md",
          "answer.md",
        ],
      },
    ],

    // 侧边栏
    sidebar: {
      "/": [
        {
          text: "入门",
          icon: "rocket",
          expanded: true,
          children: [
            "introduction.md",
            "installation.md",
            "anaconda.md",
            "dependency.md",
            "platform.md",
          ],
        },
        {
          text: "教程与示例",
          icon: "book",
          children: [
            "tutorial.md",
            "demo.md",
            "data_tips.md",
            "indicator.md",
            "special.md",
            "trade.md",
          ],
        },
        {
          text: "增强功能 (Pro)",
          icon: "shield-halved",
          children: [
            "akshare_introduction.md",
            "akshare_help_summary.md",
          ],
        },
        {
          text: "部署",
          icon: "server",
          children: [
            "deploy_http.md",
            "akdocker/akdocker.md",
          ],
        },
        {
          text: "社区",
          icon: "people-group",
          children: [
            "contributing.md",
            "articles.md",
            "answer.md",
            "changelog.md",
          ],
        },
      ],
      "/data/": [
        {
          text: "股票数据",
          icon: "chart-line",
          children: ["stock/stock.md"],
        },
        {
          text: "期货数据",
          icon: "industry",
          children: [
            "futures/futures.md",
            "qhkc/broker.md",
            "qhkc/commodity.md",
            "qhkc/fund.md",
            "qhkc/fundamental.md",
            "qhkc/index_data.md",
            "qhkc/tools.md",
          ],
        },
        {
          text: "债券数据",
          icon: "file-invoice-dollar",
          children: ["bond/bond.md"],
        },
        {
          text: "基金数据",
          icon: "piggy-bank",
          children: [
            "fund/fund_public.md",
            "fund/fund_private.md",
            "qdii/qdii.md",
          ],
        },
        {
          text: "期权数据",
          icon: "diagram-project",
          children: ["option/option.md"],
        },
        {
          text: "外汇数据",
          icon: "money-bill-transfer",
          children: ["fx/fx.md", "currency/currency.md"],
        },
        {
          text: "宏观数据",
          icon: "earth-americas",
          children: ["macro/macro.md"],
        },
        {
          text: "指数数据",
          icon: "chart-pie",
          children: ["index/index.md"],
        },
        {
          text: "另类数据",
          icon: "cube",
          children: [
            "energy/energy.md",
            "event/event.md",
            "hf/hf.md",
            "others/others.md",
            "spot/spot.md",
            "article/article.md",
            "nlp/nlp.md",
            "dc/dc.md",
          ],
        },
        {
          text: "利率与银行",
          icon: "building-columns",
          children: [
            "interest_rate/interest_rate.md",
            "bank/bank.md",
          ],
        },
        {
          text: "工具箱",
          icon: "screwdriver-wrench",
          children: ["tool/tool.md"],
        },
      ],
    },

    // 页脚
    footer:
      'AKShare Pro — 基于 <a href="https://github.com/delon-xie/aksharepro" target="_blank">AKShare Pro</a> | <a href="https://delon-xie.github.io/aksharepro/" target="_blank">文档</a>',
    displayFooter: true,

    // 页面 meta
    metaLocales: {
      editLink: "在 GitHub 上编辑此页",
    },

    // 功能开关
    toc: true,
    print: false,

    // 插件配置
    plugins: {
      slimsearch: true,
    },
  }),

  // 打包器
  bundler: viteBundler(),
});
