# !/usr/bin/env python
"""
Date: 2026/06/06
Desc: 核心请求入口（增强版）
      集成 BrowserSessionManager，支持浏览器级伪装、Cookie 注入、智能限频
"""

import time
from typing import Callable, Dict

from requests.exceptions import RequestException

from akshare.exceptions import NetworkError, APIError, RateLimitError, DataParsingError
from akshare.utils.context import config


def _get_session_and_headers(url, headers=None, proxies=None):
    """
    内部辅助：获取 Session + 合并请求头

    :param url: 请求 URL
    :param headers: 调用方传入的额外请求头
    :param proxies: 代理设置
    :return: (session, merged_headers, proxies)
    """
    from akshare.utils.session import get_session_manager

    mgr = get_session_manager()

    # 限频
    mgr.rate_limit_wait(url)

    # 合并请求头（浏览器头 + 全局 Cookie + 用户额外头）
    merged_headers = mgr.get_merged_headers(url, extra_headers=headers)

    # Session：用户自定义 > 全局管理
    user_session = config.get_session()
    session = user_session if user_session is not None else mgr.get_session()

    # 注入 Cookie 到 Session
    mgr.inject_cookies_to_session(url, session)

    # 代理
    if proxies is None:
        proxies = config.proxies

    return session, merged_headers, proxies


def make_request_with_retry_json(
    url,
    params=None,
    headers=None,
    proxies=None,
    max_retries=3,
    retry_delay=1,
    # 新增可选参数
    cookies: Dict = None,
    progress_callback: Callable = None,
):
    """
    发送 HTTP GET 请求，支持重试机制、浏览器伪装和代理设置。

    :param url: 请求的 URL
    :param params: URL 参数 (可选)
    :param headers: 请求头 (可选，与浏览器头合并)
    :param proxies: 代理设置 (可选)
    :param max_retries: 最大重试次数
    :param retry_delay: 初始重试延迟（秒）
    :param cookies: 本次请求的 Cookie（覆盖全局）
    :param progress_callback: 进度回调 Callable[[int, str], None]
    :return: 解析后的 JSON 数据
    """
    _callback = progress_callback or config.get_progress_callback()

    session, merged_headers, proxies = _get_session_and_headers(url, headers, proxies)

    # 合并调用级 Cookie
    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        existing = merged_headers.get("Cookie", "")
        merged_headers["Cookie"] = f"{existing}; {cookie_str}" if existing else cookie_str

    current_delay = retry_delay
    for attempt in range(max_retries):
        try:
            if _callback:
                _callback(10 + attempt * 5, f"请求中... ({attempt + 1}/{max_retries})")

            response = session.get(
                url,
                params=params,
                headers=merged_headers,
                proxies=proxies,
                timeout=15,
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    if not data:
                        raise DataParsingError("Empty response data")
                    if _callback:
                        _callback(50, "JSON 解析成功")
                    return data
                except ValueError:
                    raise DataParsingError("Failed to parse JSON response")
            elif response.status_code == 429:
                raise RateLimitError(
                    f"Rate limit exceeded. Status code: {response.status_code}"
                )
            else:
                raise APIError(
                    f"API request failed. Status code: {response.status_code}"
                )

        except (RequestException, RateLimitError, APIError, DataParsingError) as e:
            if attempt == max_retries - 1:
                if isinstance(e, RateLimitError):
                    raise
                elif isinstance(e, (APIError, DataParsingError)):
                    raise
                else:
                    raise NetworkError(
                        f"Failed to connect after {max_retries} attempts: {str(e)}"
                    )

            time.sleep(current_delay)
            current_delay *= 2  # 指数退避策略

    raise NetworkError(f"Failed to connect after {max_retries} attempts")


def make_request_with_retry_text(
    url,
    params=None,
    headers=None,
    proxies=None,
    max_retries=3,
    retry_delay=1,
    # 新增可选参数
    cookies: Dict = None,
    progress_callback: Callable = None,
):
    """
    发送 HTTP GET 请求，支持重试机制、浏览器伪装和代理设置，返回文本。

    :param url: 请求的 URL
    :param params: URL 参数 (可选)
    :param headers: 请求头 (可选，与浏览器头合并)
    :param proxies: 代理设置 (可选)
    :param max_retries: 最大重试次数
    :param retry_delay: 初始重试延迟（秒）
    :param cookies: 本次请求的 Cookie（覆盖全局）
    :param progress_callback: 进度回调 Callable[[int, str], None]
    :return: 响应文本
    """
    _callback = progress_callback or config.get_progress_callback()

    session, merged_headers, proxies = _get_session_and_headers(url, headers, proxies)

    # 合并调用级 Cookie
    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        existing = merged_headers.get("Cookie", "")
        merged_headers["Cookie"] = f"{existing}; {cookie_str}" if existing else cookie_str

    current_delay = retry_delay
    for attempt in range(max_retries):
        try:
            if _callback:
                _callback(10 + attempt * 5, f"请求中... ({attempt + 1}/{max_retries})")

            response = session.get(
                url,
                params=params,
                headers=merged_headers,
                proxies=proxies,
                timeout=15,
            )

            if response.status_code == 200:
                try:
                    data = response.text
                    if not data:
                        raise DataParsingError("Empty response data")
                    if _callback:
                        _callback(50, "文本获取成功")
                    return data
                except ValueError:
                    raise DataParsingError("Failed to parse text response")
            elif response.status_code == 429:
                raise RateLimitError(
                    f"Rate limit exceeded. Status code: {response.status_code}"
                )
            else:
                raise APIError(
                    f"API request failed. Status code: {response.status_code}"
                )

        except (RequestException, RateLimitError, APIError, DataParsingError) as e:
            if attempt == max_retries - 1:
                if isinstance(e, RateLimitError):
                    raise
                elif isinstance(e, (APIError, DataParsingError)):
                    raise
                else:
                    raise NetworkError(
                        f"Failed to connect after {max_retries} attempts: {str(e)}"
                    )

            time.sleep(current_delay)
            current_delay *= 2  # 指数退避策略

    raise NetworkError(f"Failed to connect after {max_retries} attempts")
