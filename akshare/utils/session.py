# !/usr/bin/env python
"""
Date: 2026/06/06
Desc: 浏览器级会话管理器
      提供 per-host 浏览器请求头、Cookie 注入、智能限频、Session 复用
"""

import random
import time
import threading
from typing import Dict, Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ── Per-host 浏览器请求头模板 ─────────────────────────────────────
# 模拟 Chrome/Edge 最新版本的请求头，覆盖主要数据源站点
_BROWSER_HEADERS_COMMON = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;"
        "q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "",  # 禁用压缩，避免手动解压
    "Connection": "keep-alive",
    "Sec-Ch-Ua": '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
)

HOST_HEADERS: Dict[str, Dict[str, str]] = {
    # ── 东方财富 ──────────────────────────────────────────────────
    "eastmoney.com": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://quote.eastmoney.com/",
        "Origin": "https://quote.eastmoney.com",
        **_BROWSER_HEADERS_COMMON,
    },
    # ── 新浪财经 ──────────────────────────────────────────────────
    "sina.com.cn": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://finance.sina.com.cn/",
        "Accept-Encoding": "",  # 新浪常返回 GBK 明文
        **{k: v for k, v in _BROWSER_HEADERS_COMMON.items() if k != "Accept-Encoding"},
    },
    "sinajs.cn": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://finance.sina.com.cn/",
        "Accept-Encoding": "",
        **{k: v for k, v in _BROWSER_HEADERS_COMMON.items() if k != "Accept-Encoding"},
    },
    # ── 雪球 ─────────────────────────────────────────────────────
    "xueqiu.com": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://xueqiu.com/",
        **_BROWSER_HEADERS_COMMON,
    },
    # ── 腾讯财经 ──────────────────────────────────────────────────
    "qq.com": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://web.sqt.gtimg.cn/",
        **_BROWSER_HEADERS_COMMON,
    },
    # ── 同花顺 ────────────────────────────────────────────────────
    "10jqka.com.cn": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://data.10jqka.com.cn/",
        **_BROWSER_HEADERS_COMMON,
    },
    # ── 巨潮资讯 ──────────────────────────────────────────────────
    "cninfo.com.cn": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://webapi.cninfo.com.cn/",
        **_BROWSER_HEADERS_COMMON,
    },
    # ── 中国外汇交易中心 ──────────────────────────────────────────
    "chinamoney.com.cn": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://www.chinamoney.com.cn/",
        **_BROWSER_HEADERS_COMMON,
    },
    # ── 交易所 ────────────────────────────────────────────────────
    "sse.com.cn": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://www.sse.com.cn/",
        **_BROWSER_HEADERS_COMMON,
    },
    "szse.cn": {
        "User-Agent": _USER_AGENT,
        "Referer": "https://www.szse.cn/",
        **_BROWSER_HEADERS_COMMON,
    },
    # ── 默认 ─────────────────────────────────────────────────────
    "__default__": {
        "User-Agent": _USER_AGENT,
        **_BROWSER_HEADERS_COMMON,
    },
}

# ── 默认限频配置 (秒) ────────────────────────────────────────────
_DEFAULT_RATE_LIMITS: Dict[str, tuple] = {
    "eastmoney.com": (1.5, 3.0),
    "sina.com.cn": (0.5, 1.5),
    "sinajs.cn": (0.5, 1.5),
    "xueqiu.com": (0.8, 2.0),
    "__default__": (0.3, 1.0),
}


class BrowserSessionManager:
    """
    全局浏览器级会话管理器（单例）

    核心职责:
    1. 维护 per-host 浏览器级请求头
    2. 管理全局 Session 实例（连接池复用）
    3. 自动注入用户 Cookie
    4. 智能 per-host 限频
    5. 支持用户自定义 Session 覆盖
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._session: Optional[requests.Session] = None
        self._last_request_time: Dict[str, float] = {}
        self._host_headers = HOST_HEADERS
        self._default_rate_limits = _DEFAULT_RATE_LIMITS
        self._lock = threading.Lock()

    def get_session(self) -> requests.Session:
        """
        获取 Session 实例

        优先级:
        1. 用户通过 ak.set_session() 注入的自定义 Session
        2. 全局管理的 Session（连接池复用）
        """
        from akshare.utils.context import config

        # 用户自定义 Session 优先
        user_session = config.get_session()
        if user_session is not None:
            return user_session

        # 全局管理的 Session
        if self._session is None:
            self._session = self._create_session()
        return self._session

    def _create_session(self) -> requests.Session:
        """创建带连接池和重试策略的 Session"""
        session = requests.Session()

        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=10,
            pool_maxsize=20,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def get_headers(self, url: str) -> Dict[str, str]:
        """
        根据 URL host 返回浏览器级请求头

        :param url: 请求 URL
        :return: 请求头字典
        """
        host = (urlparse(url).hostname or "").lower()

        # 匹配 per-host 请求头
        matched_headers = self._host_headers.get("__default__", {}).copy()
        for pattern, headers in self._host_headers.items():
            if pattern != "__default__" and pattern in host:
                matched_headers = headers.copy()
                break

        return matched_headers

    def get_merged_headers(self, url: str, extra_headers: Optional[Dict] = None) -> Dict[str, str]:
        """
        获取合并后的请求头（浏览器头 + 用户 Cookie + 额外头）

        :param url: 请求 URL
        :param extra_headers: 调用方传入的额外请求头
        :return: 最终请求头
        """
        from akshare.utils.context import config

        # 1. 浏览器基础头
        headers = self.get_headers(url)

        # 2. 合并用户全局 Cookie
        host = (urlparse(url).hostname or "").lower()
        cookies = config.get_cookies(host)
        if cookies:
            cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
            existing_cookie = headers.get("Cookie", "")
            if existing_cookie:
                headers["Cookie"] = f"{existing_cookie}; {cookie_str}"
            else:
                headers["Cookie"] = cookie_str

        # 3. 合并调用方传入的额外头（最高优先级）
        if extra_headers:
            headers.update(extra_headers)

        return headers

    def inject_cookies_to_session(self, url: str, session: requests.Session):
        """将用户 Cookie 注入到 Session 中"""
        from akshare.utils.context import config

        host = (urlparse(url).hostname or "").lower()
        cookies = config.get_cookies(host)
        for k, v in cookies.items():
            session.cookies.set(k, v)

    def rate_limit_wait(self, url: str):
        """
        per-host 智能限频

        :param url: 请求 URL
        """
        from akshare.utils.context import config

        host = (urlparse(url).hostname or "").lower()

        # 获取限频配置：用户自定义 > 默认
        user_limit = config.get_rate_limit(host)
        if user_limit:
            min_delay, max_delay = user_limit
        else:
            min_delay, max_delay = self._default_rate_limits.get("__default__", (0.3, 1.0))
            for pattern, limits in self._default_rate_limits.items():
                if pattern != "__default__" and pattern in host:
                    min_delay, max_delay = limits
                    break

        with self._lock:
            last_time = self._last_request_time.get(host, 0)
            elapsed = time.time() - last_time
            delay = random.uniform(min_delay, max_delay)

            if elapsed < delay:
                time.sleep(delay - elapsed)

            self._last_request_time[host] = time.time()

    def reset_session(self):
        """重置全局 Session（连接池清空）"""
        if self._session is not None:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None

    def reset_rate_limit_state(self):
        """重置限频状态"""
        with self._lock:
            self._last_request_time.clear()


# ── 模块级便捷函数 ────────────────────────────────────────────────
def get_session_manager() -> BrowserSessionManager:
    """获取全局 BrowserSessionManager 单例"""
    return BrowserSessionManager()
