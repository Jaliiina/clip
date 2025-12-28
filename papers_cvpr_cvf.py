# crawlers/papers_cvpr_cvf.py
from __future__ import annotations
import re, time, random
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -----------------------------
# 网络层（禁代理 / 关闭 keep-alive / 自动重试）
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
        "Connection": "close",           # 关键：关闭长连接，避免半开
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
    """稳健 GET：带随机退避与编码修正。"""
    time.sleep(random.uniform(*jitter))
    resp = RS.get(url, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text

# -----------------------------
# CVPR 入口与年份探测
# -----------------------------
MENU = "https://openaccess.thecvf.com/menu"
YEAR_RANGE = range(2017, 2026)  # 可按需调整

def list_cvpr_years() -> List[int]:
    """从菜单页解析可用年份，失败则回退固定范围。"""
    years: List[int] = []
    try:
        html = _get(MENU)
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select("a[href*='CVPR20'], a[href*='cvpr20']"):
            h = a.get("href") or ""
            m = re.search(r"[Cc][Vv][Pp][Rr](20\d{2})", h)
            if m:
                years.append(int(m.group(1)))
    except Exception:
        return list(YEAR_RANGE)
    years = [y for y in set(years) if y in YEAR_RANGE]
    return sorted(years)

def _cvpr_year_entry(year: int) -> Optional[str]:
    """
    返回该年的入口URL：
    先试 day=all；不行就 day=1..7；都不行返回 None。
    """
    base = f"https://openaccess.thecvf.com/CVPR{year}"
    # 先试 day=all
    try:
        _get(f"{base}?day=all")
        return f"{base}?day=all"
    except Exception:
        pass
    # 再试 day=1..7
    for d in range(1, 8):
        try:
            _get(f"{base}?day={d}")
            return f"{base}?day={d}"
        except Exception:
            continue
    return None

# -----------------------------
# 解析页面：兼容旧/新路径与大小写
# -----------------------------
def _extract_papers_from_html(html: str, year: int, fast: bool = True) -> List[Dict]:
    """
    从列表页HTML抽取条目：
    - 主要结构：<dt class="ptitle"><a ...>Title</a></dt>
    - 兼容大小写与不同content路径（/content/CVPR2024/html/... 或 /content_cvpr_2017/html/...）
    - fast=True 时不再逐条进详情页（DOI/摘要留空）
    """
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict] = []

    # 选择器1：标准 ptitle
    anchors = soup.select("dt.ptitle a[href]")
    # 选择器2：兜底（直接匹配 content 路径，大小写不敏感）
    if not anchors:
        anchors = soup.select("a[href*='/content/CVPR'], a[href*='/content_cvpr']")

    for a in anchors:
        title = (a.get("title") or a.get_text(" ", strip=True)).strip()
        href = a.get("href") or ""
        if not title or not href:
            continue
        if href.startswith("/"):
            href = "https://openaccess.thecvf.com" + href

        doi, abstract = "", ""
        # fast 模式直接跳过详情页
        if not fast:
            try:
                ph = _get(href, jitter=(0.02, 0.08))
                ps = BeautifulSoup(ph, "lxml")
                doi_a = ps.select_one("a[href*='doi.org/']")
                if doi_a:
                    doi = doi_a.get_text(" ", strip=True)
                # CVF一般不提供摘要，保持空
            except Exception as e:
                print(f"[CVPR][WARN] detail failed: {href} | {e}")

        rows.append({
            "title": title,
            "abstract": abstract,
            "url": href,
            "doi": doi,
            "year": year,
            "venue": "CVPR",
            "pub_date_raw": str(year),
        })

    # 去重（按标题）
    uniq: Dict[str, Dict] = {}
    for p in rows:
        if p.get("title"):
            uniq.setdefault(p["title"], p)
    return list(uniq.values())

# -----------------------------
# DBLP 兜底：保证有数据
# -----------------------------
def crawl_cvpr_dblp(year: int) -> List[Dict]:
    url = f"https://dblp.org/db/conf/cvpr/cvpr{year}.html"
    try:
        html = _get(url)
    except Exception as e:
        print(f"[CVPR][DBLP] {year} fetch failed: {e}")
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
            "url": href,              # 可能是出版社/Anthology链接
            "doi": "",
            "year": year,
            "venue": "CVPR",
            "pub_date_raw": str(year),
        })
    # 去重
    uniq: Dict[str, Dict] = {}
    for p in rows:
        if p.get("title"):
            uniq.setdefault(p["title"], p)
    return list(uniq.values())

# -----------------------------
# 按年抓取（CVF→DBLP 兜底）
# -----------------------------
def crawl_cvpr_year(year: int, fast: bool = True) -> List[Dict]:
    entry = _cvpr_year_entry(year)
    if entry:
        try:
            html = _get(entry)
            rows = _extract_papers_from_html(html, year, fast=fast)
            # 如果 day!=all，尝试再合并 day=all（有些年 day=all 才全）
            if "day=" in entry and "all" not in entry:
                try:
                    html_all = _get(entry.rsplit("=", 1)[0] + "=all")
                    rows_all = _extract_papers_from_html(html_all, year, fast=fast)
                    # 合并去重
                    have = {r["title"] for r in rows}
                    for r in rows_all:
                        if r["title"] not in have:
                            rows.append(r)
                except Exception:
                    pass
            if rows:
                return rows
            else:
                print(f"[CVPR] {year}: CVF returned 0 -> fallback DBLP")
        except Exception as e:
            print(f"[CVPR][WARN] {year} CVF failed: {e} -> fallback DBLP")
    # 兜底
    return crawl_cvpr_dblp(year)

def crawl_cvpr(year_start=2017, year_end=2025, fast: bool = True) -> List[Dict]:
    years = [y for y in list_cvpr_years() if year_start <= y <= year_end]
    print(f"[CVPR] years: {years}")
    all_rows: List[Dict] = []
    for y in years:
        rs = crawl_cvpr_year(y, fast=fast)
        print(f"[CVPR] {y}: {len(rs)}")
        all_rows.extend(rs)
        time.sleep(random.uniform(0.05, 0.15))
    # 总去重
    uniq: Dict[str, Dict] = {}
    for p in all_rows:
        if p.get("title"):
            uniq.setdefault(p["title"], p)
    return list(uniq.values())

# -----------------------------
# 独立运行入口：写入 raw CSV
# -----------------------------
if __name__ == "__main__":
    from core.sink import save_papers
    rows = crawl_cvpr(2017, 2025, fast=True)  # 快跑，不进详情页
    save_papers("cvpr", rows, mode="w")
    print("[CVPR] done.")
