# !/usr/bin/env python
"""
Date: 2025/12/31
Desc: HTTP 请求工具函数
      增强版：集成 BrowserSessionManager，支持浏览器级伪装、Cookie 注入、
      进度回调、断点续传、智能限频
"""

import pickle
import random
import time
from typing import Callable, Dict, Tuple

import requests


def request_with_retry(
    url: str,
    params: Dict = None,
    timeout: int = 15,
    max_retries: int = 3,
    base_delay: float = 1.0,
    random_delay_range: Tuple[float, float] = (0.5, 1.5),
    # --- 新增参数（全部可选，默认从全局 config 获取）---
    cookies: Dict = None,
    progress_callback: Callable = None,
    resume_key: str = None,
    session: requests.Session = None,
    headers: Dict = None,
) -> requests.Response:
    """
    带重试机制的 HTTP GET 请求（增强版）

    新增功能:
    - 自动使用 BrowserSessionManager 提供浏览器级请求头
    - 支持全局 / 调用级 Cookie 注入
    - 支持全局 / 调用级进度回调
    - 支持断点续传（通过 resume_key 标识）
    - 智能 per-host 限频

    :param url: 请求 URL
    :param params: 请求参数
    :param timeout: 超时时间（秒）
    :param max_retries: 最大重试次数
    :param base_delay: 基础延迟时间（秒），用于指数退避
    :param random_delay_range: 随机延迟范围（秒）
    :param cookies: 本次请求的 Cookie（覆盖全局 Cookie）
    :param progress_callback: 进度回调 Callable[[int, str], None]（覆盖全局回调）
    :param resume_key: 断点续传标识（传入时启用断点续传）
    :param session: 本次请求的 Session（覆盖全局 Session）
    :param headers: 额外请求头（与浏览器头合并）
    :return: Response 对象
    :raises: 最后一次请求的异常
    """
    from akshare.utils.context import config as global_config
    from akshare.utils.session import get_session_manager

    mgr = get_session_manager()

    # ── 解析全局配置 ────────────────────────────────────────────
    _cookies = cookies if cookies is not None else {}
    _callback = progress_callback or global_config.get_progress_callback()
    _session = session or global_config.get_session()

    # ── 断点续传：检查是否有可恢复状态 ─────────────────────────
    _checkpoint_enabled, _checkpoint_dir = global_config.get_checkpoint()
    _state_file = None
    _resume_data = None

    if resume_key and _checkpoint_enabled:
        from pathlib import Path
        _state_dir = Path(_checkpoint_dir)
        _state_dir.mkdir(parents=True, exist_ok=True)
        _state_file = _state_dir / f"{resume_key}.state"

        if _state_file.exists():
            try:
                with open(_state_file, "rb") as f:
                    _resume_data = pickle.load(f)
                # 24 小时过期
                if time.time() - _resume_data.get("timestamp", 0) > 86400:
                    _resume_data = None
                elif _callback:
                    _callback(5, f"[resume] 恢复进度: {_resume_data.get('current_page', '?')}")
            except Exception:
                _resume_data = None

    # ── 限频等待 ────────────────────────────────────────────────
    mgr.rate_limit_wait(url)

    # ── 构建请求头 ──────────────────────────────────────────────
    merged_headers = mgr.get_merged_headers(url, extra_headers=headers)

    # 合并调用级 Cookie
    if _cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in _cookies.items())
        existing = merged_headers.get("Cookie", "")
        merged_headers["Cookie"] = f"{existing}; {cookie_str}" if existing else cookie_str

    # ── 获取 Session ────────────────────────────────────────────
    use_session = _session if _session is not None else mgr.get_session()

    # 注入 Cookie 到 Session
    if _cookies:
        for k, v in _cookies.items():
            use_session.cookies.set(k, v)
    else:
        mgr.inject_cookies_to_session(url, use_session)

    # ── 代理 ────────────────────────────────────────────────────
    proxies = global_config.proxies

    # ── 发起请求（带重试）──────────────────────────────────────
    last_exception = None

    for attempt in range(max_retries):
        try:
            if _callback:
                _callback(
                    10 + attempt * 5,
                    f"请求中... (attempt {attempt + 1}/{max_retries})"
                )

            response = use_session.get(
                url,
                params=params,
                headers=merged_headers,
                timeout=timeout,
                proxies=proxies,
            )
            response.raise_for_status()

            if _callback:
                _callback(50, "请求成功")

            # ── 断点续传：保存成功状态 ──────────────────────────
            if _state_file and _resume_data:
                _save_checkpoint(_state_file, resume_key, url, params, _resume_data)

            return response

        except (requests.RequestException, ValueError) as e:
            last_exception = e

            if attempt < max_retries - 1:
                # 指数退避 + 随机抖动
                delay = base_delay * (2 ** attempt) + random.uniform(*random_delay_range)
                time.sleep(delay)

                # 再次限频（避免连续请求触发封禁）
                mgr.rate_limit_wait(url)

    # ── 断点续传：保存失败状态 ──────────────────────────────────
    if _state_file:
        _save_checkpoint_error(
            _state_file, resume_key, url, params, _resume_data, str(last_exception)
        )

    raise last_exception


def _save_checkpoint(state_file, resume_key, url, params, resume_data):
    """保存断点续传状态"""
    try:
        import time as _time
        state = dict(resume_data) if resume_data else {}
        state.update({
            "timestamp": _time.time(),
            "url": url,
            "params": params,
            "resume_key": resume_key,
        })
        with open(state_file, "wb") as f:
            pickle.dump(state, f)
    except Exception:
        pass


def _save_checkpoint_error(state_file, resume_key, url, params, resume_data, error_msg):
    """保存失败时的断点续传状态"""
    try:
        import time as _time
        state = dict(resume_data) if resume_data else {}
        state.update({
            "timestamp": _time.time(),
            "url": url,
            "params": params,
            "resume_key": resume_key,
            "error": error_msg,
        })
        with open(state_file, "wb") as f:
            pickle.dump(state, f)
    except Exception:
        pass
