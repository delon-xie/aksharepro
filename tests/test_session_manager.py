# !/usr/bin/env python
"""
Date: 2026/06/06
Desc: BrowserSessionManager 及增强请求层 单元测试
      直接导入子模块，绕过 __init__.py 的大量依赖导入
"""

import os
import pickle
import sys
import tempfile
import time
from unittest.mock import MagicMock, patch

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ── 阻止 akshare.__init__.py 触发大量导入 ───────────────────────
# 预注册一个空的 akshare 包模块
import types  # noqa: E402

_akshare_pkg = types.ModuleType("akshare")
_akshare_pkg.__path__ = [os.path.join(_PROJECT_ROOT, "akshare")]
_akshare_pkg.__package__ = "akshare"
sys.modules["akshare"] = _akshare_pkg

# ── 被测模块（子包直接导入，不触发 __init__.py）─────────────────
import importlib  # noqa: E402

# exceptions
_exc_spec = importlib.util.spec_from_file_location(
    "akshare.exceptions",
    os.path.join(_PROJECT_ROOT, "akshare", "exceptions.py"),
)
_exc_mod = importlib.util.module_from_spec(_exc_spec)
sys.modules["akshare.exceptions"] = _exc_mod
_exc_spec.loader.exec_module(_exc_mod)

# utils 子包
_utils_pkg = types.ModuleType("akshare.utils")
_utils_pkg.__path__ = [os.path.join(_PROJECT_ROOT, "akshare", "utils")]
_utils_pkg.__package__ = "akshare.utils"
sys.modules["akshare.utils"] = _utils_pkg

# context
_ctx_spec = importlib.util.spec_from_file_location(
    "akshare.utils.context",
    os.path.join(_PROJECT_ROOT, "akshare", "utils", "context.py"),
)
_ctx_mod = importlib.util.module_from_spec(_ctx_spec)
sys.modules["akshare.utils.context"] = _ctx_mod
_ctx_spec.loader.exec_module(_ctx_mod)

# session
_sess_spec = importlib.util.spec_from_file_location(
    "akshare.utils.session",
    os.path.join(_PROJECT_ROOT, "akshare", "utils", "session.py"),
)
_sess_mod = importlib.util.module_from_spec(_sess_spec)
sys.modules["akshare.utils.session"] = _sess_mod
_sess_spec.loader.exec_module(_sess_mod)

# request (utils/request.py)
_req_spec = importlib.util.spec_from_file_location(
    "akshare.utils.request",
    os.path.join(_PROJECT_ROOT, "akshare", "utils", "request.py"),
)
_req_mod = importlib.util.module_from_spec(_req_spec)
sys.modules["akshare.utils.request"] = _req_mod
_req_spec.loader.exec_module(_req_mod)

# request.py (顶层)
_topreq_spec = importlib.util.spec_from_file_location(
    "akshare.request",
    os.path.join(_PROJECT_ROOT, "akshare", "request.py"),
)
_topreq_mod = importlib.util.module_from_spec(_topreq_spec)
sys.modules["akshare.request"] = _topreq_mod
_topreq_spec.loader.exec_module(_topreq_mod)

# ── 提取符号 ─────────────────────────────────────────────────────
AkshareConfig = _ctx_mod.AkshareConfig
config = _ctx_mod.config
set_cookies = _ctx_mod.set_cookies
get_cookies = _ctx_mod.get_cookies
clear_cookies = _ctx_mod.clear_cookies
set_session = _ctx_mod.set_session
get_session = _ctx_mod.get_session
set_progress_callback = _ctx_mod.set_progress_callback
get_progress_callback = _ctx_mod.get_progress_callback
set_rate_limit = _ctx_mod.set_rate_limit
set_checkpoint = _ctx_mod.set_checkpoint
CookieContext = _ctx_mod.CookieContext
SessionContext = _ctx_mod.SessionContext
ProxyContext = _ctx_mod.ProxyContext

BrowserSessionManager = _sess_mod.BrowserSessionManager
get_session_manager = _sess_mod.get_session_manager
HOST_HEADERS = _sess_mod.HOST_HEADERS

CheckpointError = _exc_mod.CheckpointError

import pytest  # noqa: E402
import requests  # noqa: E402


# ── Fixture: 每个测试前重置单例状态 ─────────────────────────────
@pytest.fixture(autouse=True)
def _reset_singletons():
    """确保每个测试用例都在干净状态下运行"""
    yield
    AkshareConfig._instance = None
    BrowserSessionManager._instance = None


# ═══════════════════════════════════════════════════════════════════
# 1. AkshareConfig 单例测试
# ═══════════════════════════════════════════════════════════════════

class TestAkshareConfig:
    def test_singleton(self):
        c1 = AkshareConfig()
        c2 = AkshareConfig()
        assert c1 is c2

    def test_set_get_cookies_dict(self):
        set_cookies({"token": "abc123"})
        cookies = get_cookies()
        assert cookies == {"token": "abc123"}

    def test_set_get_cookies_string(self):
        set_cookies("key1=val1; key2=val2")
        cookies = get_cookies()
        assert cookies == {"key1": "val1", "key2": "val2"}

    def test_set_cookies_per_host(self):
        set_cookies({"xq_a": "xxx"}, host="xueqiu.com")
        assert get_cookies() == {}
        assert get_cookies(host="xueqiu.com") == {"xq_a": "xxx"}

    def test_clear_cookies(self):
        set_cookies({"a": "1"})
        set_cookies({"b": "2"}, host="example.com")
        clear_cookies()
        assert get_cookies() == {}

    def test_clear_cookies_per_host(self):
        set_cookies({"a": "1"})
        set_cookies({"b": "2"}, host="example.com")
        clear_cookies(host="example.com")
        assert get_cookies() == {"a": "1"}

    def test_set_get_session(self):
        s = requests.Session()
        set_session(s)
        assert get_session() is s
        set_session(None)
        assert get_session() is None

    def test_set_get_progress_callback(self):
        def _noop_cb(pct, msg):
            pass

        set_progress_callback(_noop_cb)
        assert get_progress_callback() is _noop_cb
        set_progress_callback(None)
        assert get_progress_callback() is None

    def test_set_rate_limit(self):
        set_rate_limit("eastmoney.com", 1.0, 3.0)
        assert AkshareConfig().get_rate_limit("eastmoney.com") == (1.0, 3.0)
        assert AkshareConfig().get_rate_limit("unknown.com") is None

    def test_set_checkpoint(self):
        set_checkpoint(True, "/tmp/test_ckpt")
        enabled, directory = AkshareConfig().get_checkpoint()
        assert enabled is True
        assert directory == "/tmp/test_ckpt"

    def test_proxies(self):
        config.set_proxies({"http": "http://127.0.0.1:7890"})
        assert config.get_proxies() == {"http": "http://127.0.0.1:7890"}


# ═══════════════════════════════════════════════════════════════════
# 2. 上下文管理器测试
# ═══════════════════════════════════════════════════════════════════

class TestContextManagers:
    def test_cookie_context(self):
        set_cookies({"existing": "old"})
        with CookieContext({"temp": "new"}, host="test.com"):
            # get_cookies(host=...) 会合并全局 Cookie
            merged = get_cookies(host="test.com")
            assert merged["temp"] == "new"
        # 退出后 per-host Cookie 被清除，只剩全局
        assert get_cookies(host="test.com") == {"existing": "old"}

    def test_session_context(self):
        s1 = requests.Session()
        s2 = requests.Session()
        set_session(s1)
        with SessionContext(s2):
            assert get_session() is s2
        assert get_session() is s1

    def test_proxy_context(self):
        config.set_proxies({"http": "old"})
        with ProxyContext({"http": "new"}):
            assert config.get_proxies() == {"http": "new"}
        assert config.get_proxies() == {"http": "old"}


# ═══════════════════════════════════════════════════════════════════
# 3. BrowserSessionManager 测试
# ═══════════════════════════════════════════════════════════════════

class TestBrowserSessionManager:
    def test_singleton(self):
        m1 = BrowserSessionManager()
        m2 = BrowserSessionManager()
        assert m1 is m2

    def test_get_headers_eastmoney(self):
        mgr = get_session_manager()
        headers = mgr.get_headers("https://push2.eastmoney.com/api/qt/clist/get")
        assert "User-Agent" in headers
        assert "Chrome" in headers["User-Agent"]
        assert "Referer" in headers
        assert "eastmoney" in headers["Referer"]

    def test_get_headers_sina(self):
        mgr = get_session_manager()
        headers = mgr.get_headers("https://hq.sinajs.cn/list=sh000001")
        assert "sina" in headers.get("Referer", "")

    def test_get_headers_xueqiu(self):
        mgr = get_session_manager()
        headers = mgr.get_headers("https://xueqiu.com/v4/statuses/public_timeline.json")
        assert "xueqiu" in headers.get("Referer", "")

    def test_get_headers_default(self):
        mgr = get_session_manager()
        headers = mgr.get_headers("https://unknown-site.example.com/api")
        assert "User-Agent" in headers
        assert "Chrome" in headers["User-Agent"]

    def test_get_session_returns_session(self):
        mgr = get_session_manager()
        s = mgr.get_session()
        assert isinstance(s, requests.Session)

    def test_get_session_user_override(self):
        user_session = requests.Session()
        set_session(user_session)
        mgr = get_session_manager()
        assert mgr.get_session() is user_session

    def test_get_merged_headers_with_cookie(self):
        set_cookies({"token": "abc"}, host="eastmoney.com")
        mgr = get_session_manager()
        headers = mgr.get_merged_headers("https://push2.eastmoney.com/api")
        assert "Cookie" in headers
        assert "token=abc" in headers["Cookie"]

    def test_get_merged_headers_extra_headers(self):
        mgr = get_session_manager()
        headers = mgr.get_merged_headers(
            "https://example.com/api",
            extra_headers={"X-Custom": "value"},
        )
        assert headers["X-Custom"] == "value"

    def test_inject_cookies_to_session(self):
        set_cookies({"my_cookie": "val123"}, host="eastmoney.com")
        mgr = get_session_manager()
        s = requests.Session()
        mgr.inject_cookies_to_session("https://push2.eastmoney.com/api", s)
        assert s.cookies.get("my_cookie") == "val123"

    def test_rate_limit_wait(self):
        mgr = get_session_manager()
        mgr.reset_rate_limit_state()
        t0 = time.time()
        mgr.rate_limit_wait("https://push2.eastmoney.com/api")
        elapsed = time.time() - t0
        assert elapsed < 1.0

    def test_reset_session(self):
        mgr = get_session_manager()
        s1 = mgr.get_session()
        mgr.reset_session()
        s2 = mgr.get_session()
        assert s1 is not s2

    def test_host_headers_coverage(self):
        expected_hosts = [
            "eastmoney.com", "sina.com.cn", "xueqiu.com",
            "qq.com", "10jqka.com.cn", "cninfo.com.cn",
        ]
        for host in expected_hosts:
            assert host in HOST_HEADERS, f"缺少 {host} 的请求头模板"


# ═══════════════════════════════════════════════════════════════════
# 4. CheckpointError 测试
# ═══════════════════════════════════════════════════════════════════

class TestCheckpointError:
    def test_checkpoint_error(self):
        err = CheckpointError("test failure", resume_key="my_key")
        assert "test failure" in str(err)
        assert err.resume_key == "my_key"

    def test_checkpoint_error_no_key(self):
        err = CheckpointError("no key")
        assert err.resume_key is None


# ═══════════════════════════════════════════════════════════════════
# 5. request_with_retry 增强版测试
# ═══════════════════════════════════════════════════════════════════

class TestRequestWithRetry:
    def test_uses_browser_headers(self):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            _sess_mod.BrowserSessionManager, "get_merged_headers",
            return_value={"User-Agent": "TestBrowser"},
        ), patch.object(
            _sess_mod.BrowserSessionManager, "get_session",
            return_value=requests.Session(),
        ), patch.object(
            _sess_mod.BrowserSessionManager, "rate_limit_wait",
        ), patch.object(
            _sess_mod.BrowserSessionManager, "inject_cookies_to_session",
        ), patch.object(
            requests.Session, "get", return_value=mock_response,
        ):
            resp = _req_mod.request_with_retry("https://example.com/api")

        assert resp.status_code == 200

    def test_progress_callback_called(self):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        callback = MagicMock()

        with patch.object(
            _sess_mod.BrowserSessionManager, "get_merged_headers", return_value={},
        ), patch.object(
            _sess_mod.BrowserSessionManager, "get_session", return_value=requests.Session(),
        ), patch.object(
            _sess_mod.BrowserSessionManager, "rate_limit_wait",
        ), patch.object(
            _sess_mod.BrowserSessionManager, "inject_cookies_to_session",
        ), patch.object(
            requests.Session, "get", return_value=mock_response,
        ):
            _req_mod.request_with_retry(
                "https://example.com/api", progress_callback=callback,
            )

        assert callback.call_count >= 1

    def test_cookies_injected_in_headers(self):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            _sess_mod.BrowserSessionManager, "get_merged_headers",
            return_value={"User-Agent": "Test"},
        ), patch.object(
            _sess_mod.BrowserSessionManager, "get_session", return_value=requests.Session(),
        ), patch.object(
            _sess_mod.BrowserSessionManager, "rate_limit_wait",
        ), patch.object(
            _sess_mod.BrowserSessionManager, "inject_cookies_to_session",
        ), patch.object(
            requests.Session, "get", return_value=mock_response,
        ) as mock_get:
            _req_mod.request_with_retry(
                "https://example.com/api",
                cookies={"my_token": "xyz"},
            )

        call_kwargs = mock_get.call_args
        sent_headers = call_kwargs.kwargs.get("headers", {})
        assert "my_token=xyz" in sent_headers.get("Cookie", "")


# ═══════════════════════════════════════════════════════════════════
# 6. make_request_with_retry 增强版测试
# ═══════════════════════════════════════════════════════════════════

class TestMakeRequestWithRetry:
    def test_json_uses_browser_session(self):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "ok"}

        with patch.object(
            _sess_mod.BrowserSessionManager, "get_merged_headers",
            return_value={"User-Agent": "BrowserTest"},
        ), patch.object(
            _sess_mod.BrowserSessionManager, "get_session", return_value=requests.Session(),
        ), patch.object(
            _sess_mod.BrowserSessionManager, "rate_limit_wait",
        ), patch.object(
            _sess_mod.BrowserSessionManager, "inject_cookies_to_session",
        ), patch.object(
            requests.Session, "get", return_value=mock_response,
        ):
            result = _topreq_mod.make_request_with_retry_json("https://example.com/api")

        assert result == {"data": "ok"}

    def test_text_uses_browser_session(self):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = "hello world"

        with patch.object(
            _sess_mod.BrowserSessionManager, "get_merged_headers",
            return_value={"User-Agent": "BrowserTest"},
        ), patch.object(
            _sess_mod.BrowserSessionManager, "get_session", return_value=requests.Session(),
        ), patch.object(
            _sess_mod.BrowserSessionManager, "rate_limit_wait",
        ), patch.object(
            _sess_mod.BrowserSessionManager, "inject_cookies_to_session",
        ), patch.object(
            requests.Session, "get", return_value=mock_response,
        ):
            result = _topreq_mod.make_request_with_retry_text("https://example.com/api")

        assert result == "hello world"


# ═══════════════════════════════════════════════════════════════════
# 7. 向后兼容性测试
# ═══════════════════════════════════════════════════════════════════

class TestBackwardCompatibility:
    def test_request_with_retry_no_new_params(self):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            _sess_mod.BrowserSessionManager, "get_merged_headers", return_value={},
        ), patch.object(
            _sess_mod.BrowserSessionManager, "get_session", return_value=requests.Session(),
        ), patch.object(
            _sess_mod.BrowserSessionManager, "rate_limit_wait",
        ), patch.object(
            _sess_mod.BrowserSessionManager, "inject_cookies_to_session",
        ), patch.object(
            requests.Session, "get", return_value=mock_response,
        ):
            resp = _req_mod.request_with_retry(
                "https://example.com/api",
                params={"key": "value"},
                timeout=10,
                max_retries=2,
            )
        assert resp.status_code == 200

    def test_make_request_no_new_params(self):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 42}

        with patch.object(
            _sess_mod.BrowserSessionManager, "get_merged_headers", return_value={},
        ), patch.object(
            _sess_mod.BrowserSessionManager, "get_session", return_value=requests.Session(),
        ), patch.object(
            _sess_mod.BrowserSessionManager, "rate_limit_wait",
        ), patch.object(
            _sess_mod.BrowserSessionManager, "inject_cookies_to_session",
        ), patch.object(
            requests.Session, "get", return_value=mock_response,
        ):
            result = _topreq_mod.make_request_with_retry_json("https://example.com/api")
        assert result == {"result": 42}


# ═══════════════════════════════════════════════════════════════════
# 8. 断点续传测试
# ═══════════════════════════════════════════════════════════════════

class TestCheckpoint:
    def test_checkpoint_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            set_checkpoint(True, tmpdir)
            state_file = os.path.join(tmpdir, "test_key.state")
            state = {
                "current_page": 5,
                "total_page": 20,
                "timestamp": time.time(),
                "url": "https://example.com",
                "params": {"pn": "1"},
            }
            with open(state_file, "wb") as f:
                pickle.dump(state, f)
            with open(state_file, "rb") as f:
                loaded = pickle.load(f)
            assert loaded["current_page"] == 5
            assert loaded["total_page"] == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
