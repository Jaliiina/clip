# crawlers/papers_emnlp_acl.py
from __future__ import annotations
import re, time, random
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -----------------------------
# 网络层（禁用系统代理、关闭 keep-alive、自动重试）
# -----------------------------
def make_session() -> requests.Session:
    s = requests.Session()
    s.trust_env = False                  # 不读取系统代理
    s.proxies = {}                       # 明确禁用代理
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "close",           # 关键：关闭长连接，避免半开挂起
    })
    retry = Retry(
        total=6, connect=6, read=6, status=6,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

RS = make_session()

def _get(url: str, timeout=(8, 30), jitter=(0.05, 0.2)) -> str:
    """稳健 GET：附带少量随机退避，显式设定编码。"""
    time.sleep(random.uniform(*jitter))
    resp = RS.get(url, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text

# -----------------------------
# 入口与卷定位
# -----------------------------
EVENT = "https://aclanthology.org/events/emnlp-{year}/"
VOL   = "https://aclanthology.org/volumes/{year}.emnlp-main/"

def _volume_url_for_year(year: int) -> Optional[str]:
    """优先直接访问 volumes/{year}.emnlp-main/；失败再去 events 页查找链接。"""
    vol = VOL.format(year=year)
    try:
        _get(vol)
        return vol
    except Exception:
        pass
    # fallback: 从 events 页解析卷链接
    try:
        ev_html = _get(EVENT.format(year=year))
        soup = BeautifulSoup(ev_html, "lxml")
        for a in soup.select("a[href]"):
            href = a.get("href") or ""
            if re.search(fr"/volumes/{year}\.emnlp-main/?$", href):
                return "https://aclanthology.org" + href if href.startswith("/") else href
    except Exception:
        return None
    return None

# -----------------------------
# 卷内抓取（fast=True 时不进详情页）
# -----------------------------
def crawl_volume(vol_url: str, year: int, fast: bool = True) -> List[Dict]:
    html = _get(vol_url)
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict] = []
    # 详情页：/{year}.emnlp-main.NNN
    for a in soup.select(f'a[href^="/{year}.emnlp-main."]'):
        href = a.get("href") or ""
        if not href.startswith("/"):
            continue
        item_url = "https://aclanthology.org" + href
        title = (a.get("title") or a.text or "").strip()
        if not title or len(title) < 3:
            continue

        doi, abstract = "", ""
        if not fast:
            try:
                ih = _get(item_url, jitter=(0.03, 0.12))
                isoup = BeautifulSoup(ih, "lxml")
                doi_a = isoup.select_one("a[href*='doi.org']")
                if doi_a:
                    doi = doi_a.get_text(" ", strip=True)
                abs_div = isoup.select_one("div#abstract")
                if abs_div:
                    abstract = abs_div.get_text(" ", strip=True)
            except Exception as e:
                print(f"[EMNLP][WARN] detail failed: {item_url} | {e}")

        rows.append({
            "title": title,
            "abstract": abstract,
            "url": item_url,
            "doi": doi,
            "year": year,
            "venue": "EMNLP",
            "pub_date_raw": str(year),  # 规范化阶段会自动补更精确日期
        })
    # 去重
    uniq: Dict[str, Dict] = {}
    for p in rows:
        if p.get("title"):
            uniq.setdefault(p["title"], p)
    return list(uniq.values())

# -----------------------------
# DBLP 兜底（ACL 不通时）
# -----------------------------
def crawl_emnlp_dblp(year: int) -> List[Dict]:
    url = f"https://dblp.org/db/conf/emnlp/emnlp{year}.html"
    try:
        html = _get(url)
    except Exception as e:
        print(f"[EMNLP][DBLP] {year} fetch failed: {e}")
        return []
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict] = []
    for li in soup.select("li.entry.inproceedings"):
        t = li.select_one("span.title")
        if not t:
            continue
        title = t.get_text(" ", strip=True)
        a = li.select_one("nav.publ a[href]")
        href = a.get("href") if a else ""
        rows.append({
            "title": title,
            "abstract": "",
            "url": href,
            "doi": "",
            "year": year,
            "venue": "EMNLP",
            "pub_date_raw": str(year),
        })
    # 去重
    uniq: Dict[str, Dict] = {}
    for p in rows:
        if p.get("title"):
            uniq.setdefault(p["title"], p)
    return list(uniq.values())

# -----------------------------
# 主流程：逐年抓取；ACL 卷失败就回退 DBLP
# -----------------------------
def crawl_emnlp(year_start=2021, year_end=2025, fast: bool = True) -> List[Dict]:
    all_rows: List[Dict] = []
    for y in range(year_start, year_end + 1):
        vol = _volume_url_for_year(y)
        year_rows: List[Dict] = []
        if vol:
            try:
                year_rows = crawl_volume(vol, y, fast=fast)
            except Exception as e:
                print(f"[EMNLP][WARN] ACL {y} failed: {e} -> fallback DBLP")
                year_rows = crawl_emnlp_dblp(y)
        else:
            print(f"[EMNLP] {y}: volume not found -> fallback DBLP")
            year_rows = crawl_emnlp_dblp(y)
        print(f"[EMNLP] {y}: {len(year_rows)}")
        all_rows.extend(year_rows)
        # 轻微降速，避免被限
        time.sleep(random.uniform(0.05, 0.15))
    # 总去重
    uniq: Dict[str, Dict] = {}
    for p in all_rows:
        if p.get("title"):
            uniq.setdefault(p["title"], p)
    return list(uniq.values())

# -----------------------------
# 独立运行入口：直接写 raw CSV
# -----------------------------
if __name__ == "__main__":
    from core.sink import save_papers
    rows = crawl_emnlp(2021, 2025, fast=True)  # 快跑：不进详情页
    save_papers("emnlp", rows, mode="w")
    print("[EMNLP] done.")
