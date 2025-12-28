# crawlers/papers_icml_pmlr.py
from __future__ import annotations
import re, time, requests
from bs4 import BeautifulSoup
from typing import List, Dict

IDX = "https://proceedings.mlr.press/"
UA = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
RS = requests.Session()
RS.headers.update(UA)
RS.timeout = 20

def _get(url: str) -> str:
    r = RS.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def list_icml_volumes() -> List[str]:
    """从 PMLR 索引页枚举卷，并仅保留“ICML”卷链接"""
    html = _get(IDX)
    soup = BeautifulSoup(html, "lxml")
    vols = []
    # PMLR 索引页是 <a href="/vXXX/">
    for a in soup.select('a[href^="/v"]'):
        href = a.get("href") or ""
        vol_url = f"https://proceedings.mlr.press{href}".rstrip("/")
        # 进入卷页检查是否 ICML（避免误抓 AISTATS/UAI/CoLLAs 等）
        try:
            vhtml = _get(vol_url + "/")
        except Exception:
            continue
        if re.search(r"\bInternational Conference on Machine Learning\b|\bICML\b", vhtml, re.I):
            vols.append(vol_url)
            time.sleep(0.3)
    # 去重并排序
    return sorted(set(vols), key=lambda x: x)

def crawl_volume(vol_url: str) -> List[Dict]:
    """在单个 ICML 卷页抓所有论文。PMLR 卷页结构：每篇论文一个 .paper 区块"""
    html = _get(vol_url + "/")
    soup = BeautifulSoup(html, "lxml")

    # 页面文本里通常能找到年份
    txt = soup.get_text(" ", strip=True)
    ym = re.search(r"(20\d{2})", txt)
    year = int(ym.group(1)) if ym else None

    rows: List[Dict] = []
    # 论文块有时是 div.paper，有时是 li.paper，也可能是 div[data-scroll-target]
    # 保险写法：找所有指向论文详情页的链接（以 /vXXX/paper-name.html 结尾）
    for a in soup.select('a[href$=".html"]'):
        href = a.get("href") or ""
        if not href.startswith("/v"):
            continue
        # 过滤非论文页（例如作者页、pdf 链接在另一个 <a>）
        if not re.match(r"^/v\d+/.+\.html$", href):
            continue
        title = a.get("title") or a.text
        if not title or len(title.strip()) < 3:
            continue
        paper_url = f"https://proceedings.mlr.press{href}"
        abstract = ""
        doi = ""

        # 进入论文详情页，抓摘要和 DOI（若有）
        try:
            ph = _get(paper_url)
            ps = BeautifulSoup(ph, "lxml")
            abs_div = ps.select_one("div.abstract")
            if abs_div:
                abstract = abs_div.get_text(" ", strip=True)
            # DOI 链接
            doi_a = ps.find("a", href=re.compile(r"doi\.org/"))
            if doi_a:
                doi = doi_a.text.strip()
        except Exception:
            pass

        rows.append({
            "title": title.strip(),
            "abstract": abstract,
            "url": paper_url,
            "doi": doi,
            "year": year,
            "venue": "ICML",
            "pub_date_raw": str(year) if year else "",
        })
        time.sleep(0.15)

    # 去重（按标题）
    uniq = {}
    for p in rows:
        uniq.setdefault(p["title"], p)
    return list(uniq.values())

# —— DBLP 兜底：若 PMLR 抓不到，直接从 DBLP 拿题录（标题+详情页+年）——
def crawl_icml_dblp(year_start=2015, year_end=2025) -> List[Dict]:
    all_rows: List[Dict] = []
    for y in range(year_start, year_end+1):
        url = f"https://dblp.org/db/conf/icml/icml{y}.html"
        try:
            h = _get(url)
        except Exception:
            continue
        s = BeautifulSoup(h, "lxml")
        # DBLP 论文条目选择器：li.entry inproceedings
        for li in s.select("li.entry.inproceedings"):
            t = li.select_one("span.title")
            if not t:
                continue
            title = t.get_text(" ", strip=True)
            # 详情页（到 anthology/pmlr 不一定有 DOI，这里主要补条数）
            a = li.select_one("nav.publ a[href]")
            href = a.get("href") if a else ""
            all_rows.append({
                "title": title,
                "abstract": "",
                "url": href,
                "doi": "",
                "year": y,
                "venue": "ICML",
                "pub_date_raw": str(y),
            })
        time.sleep(0.4)
    # 去重
    uniq = {}
    for p in all_rows:
        uniq.setdefault(p["title"], p)
    return list(uniq.values())

def crawl_icml() -> List[Dict]:
    vols = list_icml_volumes()
    if not vols:
        print("[ICML] PMLR volumes not found; fallback to DBLP.")
        return crawl_icml_dblp(2015, 2025)

    all_rows: List[Dict] = []
    print(f"[ICML] volumes detected: {len(vols)}")
    for v in vols:
        try:
            rs = crawl_volume(v)
            print(f"[ICML] {v.split('/')[-1]} -> {len(rs)}")
            all_rows.extend(rs)
        except Exception as e:
            print(f"[ICML] {v} failed: {e}")
    return all_rows

if __name__ == "__main__":
    from core.sink import save_papers
    rows = crawl_icml()
    save_papers("icml", rows, mode="w")
