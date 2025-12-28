# crawlers/netutil.py
from __future__ import annotations
import random, time, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Connection": "close",  # 关键：关闭 keep-alive，避免远端无响应的半开连接
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def make_session() -> requests.Session:
    s = requests.Session()
    s.trust_env = False      # 不继承系统代理
    s.proxies = {}           # 明确禁用代理
    s.headers.update(DEFAULT_HEADERS)

    retry = Retry(
        total=6, connect=6, read=6, status=6,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
        respect_retry_after_header=True
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

def robust_get(session: requests.Session, url: str, timeout=(8, 30), jitter=(0.05, 0.2)) -> str:
    """
    稳健 GET：内含多次尝试 + 随机退避。失败抛异常，由调用方决定是否跳过。
    """
    # 轻微随机等待，避免被判定为机器人
    time.sleep(random.uniform(*jitter))
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    # 一些站点 gzip/encoding 有问题：显式使用 apparent_encoding
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text
