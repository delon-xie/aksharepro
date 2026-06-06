# !/usr/bin/env python
"""
Date: 2026/06/06
Desc: 全局配置与上下文管理模块
      提供 Cookie/Session 注入、进度回调、限频、断点续传等全局配置能力
"""

import copy
from typing import Callable, Dict, Optional, Union

import requests


class AkshareConfig:
    """
    AKShare 全局配置单例

    支持以下配置项:
    - proxies: HTTP 代理设置
    - cookies: 全局或 per-host Cookie (dict)
    - session: 用户自定义 requests.Session 实例
    - progress_callback: 全局进度回调 Callable[[int, str], None]
    - rate_limits: per-host 限频配置 {host_pattern: (min_delay, max_delay)}
    - checkpoint_enabled: 是否启用断点续传
    - checkpoint_dir: 断点状态保存目录
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        # 原有
        self.proxies: Optional[Dict] = None
        # 新增
        self._cookies: Dict[str, Dict] = {"__global__": {}}
        self._session: Optional[requests.Session] = None
        self._progress_callback: Optional[Callable] = None
        self._rate_limits: Dict[str, tuple] = {}
        self._checkpoint_enabled: bool = False
        self._checkpoint_dir: str = "./akshare_checkpoints"
        self._session_manager = None  # 延迟初始化

    # ── proxies ──────────────────────────────────────────────────
    @classmethod
    def set_proxies(cls, proxies):
        cls().proxies = proxies

    @classmethod
    def get_proxies(cls):
        return cls().proxies

    # ── cookies ──────────────────────────────────────────────────
    @classmethod
    def set_cookies(cls, cookies: Union[Dict, str], host: Optional[str] = None):
        """
        设置 Cookie

        :param cookies: Cookie 字典或字符串
        :param host: 指定 host 时才生效，None 表示全局 Cookie
        """
        instance = cls()
        if isinstance(cookies, str):
            # 解析 "key1=val1; key2=val2" 格式
            cookie_dict = {}
            for part in cookies.split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    cookie_dict[k.strip()] = v.strip()
            cookies = cookie_dict

        key = host if host else "__global__"
        if key not in instance._cookies:
            instance._cookies[key] = {}
        instance._cookies[key].update(cookies)

    @classmethod
    def get_cookies(cls, host: Optional[str] = None) -> Dict:
        """获取 Cookie，合并全局 + per-host"""
        instance = cls()
        merged = dict(instance._cookies.get("__global__", {}))
        if host:
            for pattern, cookies in instance._cookies.items():
                if pattern != "__global__" and pattern in (host or ""):
                    merged.update(cookies)
        return merged

    @classmethod
    def clear_cookies(cls, host: Optional[str] = None):
        """清除 Cookie"""
        instance = cls()
        if host:
            instance._cookies.pop(host, None)
        else:
            instance._cookies = {"__global__": {}}

    # ── session ──────────────────────────────────────────────────
    @classmethod
    def set_session(cls, session: Optional[requests.Session]):
        """设置用户自定义 Session"""
        cls()._session = session

    @classmethod
    def get_session(cls) -> Optional[requests.Session]:
        """获取用户自定义 Session"""
        return cls()._session

    # ── progress_callback ────────────────────────────────────────
    @classmethod
    def set_progress_callback(cls, callback: Optional[Callable]):
        """设置全局进度回调 Callable[[int, str], None]"""
        cls()._progress_callback = callback

    @classmethod
    def get_progress_callback(cls) -> Optional[Callable]:
        return cls()._progress_callback

    # ── rate_limits ──────────────────────────────────────────────
    @classmethod
    def set_rate_limit(cls, host: str, min_delay: float, max_delay: float):
        """设置 per-host 限频 (秒)"""
        cls()._rate_limits[host] = (min_delay, max_delay)

    @classmethod
    def get_rate_limit(cls, host: str) -> Optional[tuple]:
        """获取 per-host 限频配置"""
        instance = cls()
        for pattern, limits in instance._rate_limits.items():
            if pattern in host:
                return limits
        return None

    # ── checkpoint ───────────────────────────────────────────────
    @classmethod
    def set_checkpoint(cls, enabled: bool, directory: str = "./akshare_checkpoints"):
        """配置断点续传"""
        instance = cls()
        instance._checkpoint_enabled = enabled
        instance._checkpoint_dir = directory

    @classmethod
    def get_checkpoint(cls) -> tuple:
        """返回 (enabled, directory)"""
        instance = cls()
        return instance._checkpoint_enabled, instance._checkpoint_dir

    # ── session_manager ──────────────────────────────────────────
    @classmethod
    def get_session_manager(cls):
        """获取 BrowserSessionManager（延迟初始化）"""
        instance = cls()
        if instance._session_manager is None:
            from akshare.utils.session import BrowserSessionManager
            instance._session_manager = BrowserSessionManager()
        return instance._session_manager

    # ── reset ────────────────────────────────────────────────────
    @classmethod
    def reset(cls):
        """重置所有配置（测试用）"""
        instance = cls()
        instance._initialized = False
        instance.__init__()
        instance._initialized = True


# 全局单例
config = AkshareConfig()


# ── 公共 API 函数 ────────────────────────────────────────────────
def set_proxies(proxies):
    """设置 HTTP 代理"""
    config.set_proxies(proxies)


def get_proxies():
    """获取 HTTP 代理"""
    return config.get_proxies()


def set_cookies(cookies: Union[Dict, str], host: Optional[str] = None):
    """
    设置 Cookie（支持全局和 per-host）

    示例::

        import akshare as ak

        # 全局 Cookie
        ak.set_cookies({"token": "abc123"})

        # per-host Cookie（雪球需要登录态）
        ak.set_cookies({"xq_a_token": "xxx"}, host="xueqiu.com")

        # 字符串格式
        ak.set_cookies("key1=val1; key2=val2", host="eastmoney.com")
    """
    config.set_cookies(cookies, host)


def get_cookies(host: Optional[str] = None) -> Dict:
    """获取 Cookie"""
    return config.get_cookies(host)


def clear_cookies(host: Optional[str] = None):
    """清除 Cookie"""
    config.clear_cookies(host)


def set_session(session: Optional[requests.Session]):
    """
    设置用户自定义 requests.Session

    示例::

        import requests
        import akshare as ak

        s = requests.Session()
        s.headers.update({"Authorization": "Bearer xxx"})
        ak.set_session(s)
    """
    config.set_session(session)


def get_session() -> Optional[requests.Session]:
    """获取用户自定义 Session"""
    return config.get_session()


def set_progress_callback(callback: Optional[Callable]):
    """
    设置全局进度回调函数

    示例::

        import akshare as ak

        def on_progress(pct: int, msg: str):
            print(f"[{pct}%] {msg}")

        ak.set_progress_callback(on_progress)
    """
    config.set_progress_callback(callback)


def get_progress_callback() -> Optional[Callable]:
    """获取进度回调函数"""
    return config.get_progress_callback()


def set_rate_limit(host: str, min_delay: float, max_delay: float):
    """
    设置 per-host 限频

    示例::

        import akshare as ak

        # 东财请求间隔 1.5~3 秒
        ak.set_rate_limit("eastmoney.com", 1.5, 3.0)
    """
    config.set_rate_limit(host, min_delay, max_delay)


def set_checkpoint(enabled: bool, directory: str = "./akshare_checkpoints"):
    """
    配置断点续传

    示例::

        import akshare as ak

        ak.set_checkpoint(True, directory="./my_checkpoints")
    """
    config.set_checkpoint(enabled, directory)


# ── 上下文管理器 ─────────────────────────────────────────────────
class ProxyContext:
    """代理上下文管理器（保留原有）"""

    def __init__(self, proxies):
        self.proxies = proxies
        self.old_proxies = None

    def __enter__(self):
        self.old_proxies = config.get_proxies()
        config.set_proxies(self.proxies)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        config.set_proxies(self.old_proxies)
        return False


class CookieContext:
    """
    Cookie 上下文管理器

    示例::

        with ak.CookieContext({"xq_a_token": "xxx"}, host="xueqiu.com"):
            df = ak.stock_xq(...)
        # 退出后自动清除
    """

    def __init__(self, cookies: Union[Dict, str], host: Optional[str] = None):
        self.cookies = cookies
        self.host = host
        self._old_cookies = None

    def __enter__(self):
        instance = AkshareConfig()
        key = self.host if self.host else "__global__"
        self._old_cookies = copy.deepcopy(instance._cookies.get(key, {}))
        config.set_cookies(self.cookies, self.host)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        instance = AkshareConfig()
        key = self.host if self.host else "__global__"
        if self._old_cookies is not None:
            instance._cookies[key] = self._old_cookies
        else:
            instance._cookies.pop(key, None)
        return False


class SessionContext:
    """
    Session 上下文管理器

    示例::

        import requests
        with ak.SessionContext(requests.Session()) as ctx:
            df = ak.stock_zh_a_hist(...)
        # 退出后自动恢复
    """

    def __init__(self, session: requests.Session):
        self.session = session
        self._old_session = None

    def __enter__(self):
        self._old_session = config.get_session()
        config.set_session(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        config.set_session(self._old_session)
        return False
