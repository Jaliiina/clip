# crawlers/papers_aaai_ojs.py
from __future__ import annotations
import re, time, requests
from bs4 import BeautifulSoup
from typing import List, Dict

from crawlers.netutil import make_session, robust_get

ARCHIVE = "https://ojs.aaai.org/index.php/AAAI/issue/archive"
UA = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
RS = make_session()
RS.headers.update(UA)


def _get(url: str, timeout=25) -> str:
    return robust_get(RS, url, timeout=(8, 30))

def list_issue_urls(year_start: int, year_end: int) -> List[str]:
    """在档案页枚举所有 issue 链接，并按年份范围过滤"""
    html = _get(ARCHIVE)
    soup = BeautifulSoup(html, "lxml")
    urls: List[str] = []
    # OJS 档案页每个期刊块通常是 .obj_issue_summary 或包含 issue 链接的 <a>
    for a in soup.select("a[href*='/issue/view/']"):
        href = a.get("href") or ""
        text = a.get_text(" ", strip=True)
        m = re.search(r"(20\d{2})", text)
        if not m:
            # 年份可能不在链接文本里，再往上层找
            parent_txt = a.find_parent().get_text(" ", strip=True) if a.find_parent() else ""
            m = re.search(r"(20\d{2})", parent_txt)
        year = int(m.group(1)) if m else None
        if year and (year_start <= year <= year_end):
            if href.startswith("/"):
                href = "https://ojs.aaai.org" + href
            urls.append(href)
    # 去重
    return sorted(set(urls))

def crawl_issue(issue_url: str, fast: bool = False) -> List[Dict]:
    html = _get(issue_url)
    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict] = []
    for art in soup.select(".obj_article_summary"):
        a = art.select_one("a.title, a.obj_galley_link, a[href*='/article/view/']")
        if not a:
            a = art.select_one("a[href*='/article/view/']")
        if not a:
            continue
        title = (a.get("title") or a.get_text(" ", strip=True)).strip()
        href = a.get("href") or ""
        if not title or not href:
            continue
        if href.startswith("/"):
            href = "https://ojs.aaai.org" + href

        doi, abstract, year, pub_raw = "", "", None, ""
        if not fast:
            try:
                ph = _get(href)
                ps = BeautifulSoup(ph, "lxml")
                doi_a = ps.select_one("a[href*='doi.org/']")
                if doi_a: doi = doi_a.get_text(" ", strip=True)
                abs_div = ps.select_one("section.item.abstract, div#articleAbstract, div.abstract")
                if abs_div: abstract = abs_div.get_text(" ", strip=True)
                txt = ps.get_text(" ", strip=True)
                m = re.search(r"(20\d{2})", txt)
                year = int(m.group(1)) if m else None
                meta_date = ps.find("meta", attrs={"name": "citation_publication_date"})
                if meta_date and meta_date.get("content"):
                    pub_raw = meta_date["content"]
            except Exception:
                pass
        rows.append({
            "title": title, "abstract": abstract, "url": href, "doi": doi,
            "year": year, "venue": "AAAI", "pub_date_raw": pub_raw or ""
        })
    return rows

def crawl_aaai(year_start=2021, year_end=2025, fast: bool = False) -> list[dict]:
    issues = list_issue_urls(year_start, year_end)
    print(f"[AAAI] issues in {year_start}-{year_end}: {len(issues)}")
    all_rows: list[dict] = []
    for u in issues:
        try:
            rs = crawl_issue(u, fast=fast)
            print(f"[AAAI] {u} -> {len(rs)}")
            all_rows.extend(rs)
        except Exception as e:
            print(f"[AAAI][WARN] issue failed: {u} | {e}")
            continue
    # 去重
    uniq = {}; [uniq.setdefault(p["title"], p) for p in all_rows if p.get("title")]
    return list(uniq.values())



if __name__ == "__main__":
    from core.sink import save_papers
    rows = crawl_aaai(2021, 2025)
    save_papers("aaai", rows, mode="w")
