# crawlers/papers_neurips.py
from __future__ import annotations
import re, time, requests
from bs4 import BeautifulSoup
from typing import List, Dict

BASE1 = "https://proceedings.neurips.cc/paper_files/paper/{year}"
BASE2 = "https://proceedings.neurips.cc/paper/{year}"
HEADERS = {"User-Agent":"Mozilla/5.0"}

def _fetch(url: str, timeout=20):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text

def list_year_index(year: int) -> str | None:
    for base in (BASE1, BASE2):
        url = base.format(year=year)
        try:
            html = _fetch(url)
            if "NeurIPS" in html or "NIPS" in html:
                return url
        except Exception:
            continue
    return None

def crawl_year(year: int) -> List[Dict]:
    url = list_year_index(year)
    if not url:
        return []
    html = _fetch(url)
    soup = BeautifulSoup(html, "lxml")
    papers = []
    for a in soup.select("a"):
        href = a.get("href") or ""
        title = a.text.strip()
        # 过滤非论文链接
        if not title or len(title) < 5:
            continue
        if not re.search(r"/paper/\d{4}/|/file/|/hash/", href):
            continue
        if href.startswith("/"):
            href = "https://proceedings.neurips.cc" + href
        papers.append({
            "title": title,
            "url": href,
            "doi": "",                 # NeurIPS页通常无DOI，后续用日期补全管线兜底
            "year": year,
            "venue": "NeurIPS",
            "pub_date_raw": str(year), # 兜底给年
        })
    # 去重（按标题）
    uniq = {}
    for p in papers:
        uniq.setdefault(p["title"], p)
    return list(uniq.values())

def crawl_neurips(year_start=2021, year_end=2025) -> List[Dict]:
    all_rows = []
    for y in range(year_start, year_end+1):
        try:
            rows = crawl_year(y)
            print(f"[NeurIPS] {y}: {len(rows)}")
            all_rows.extend(rows)
            time.sleep(0.8)
        except Exception as e:
            print(f"[NeurIPS] {y} failed: {e}")
    return all_rows

if __name__ == "__main__":
    from core.sink import save_papers
    rows = crawl_neurips()
    save_papers("neurips", rows, mode="w")
