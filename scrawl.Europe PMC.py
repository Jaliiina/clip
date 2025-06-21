import requests
import xml.etree.ElementTree as ET
import os
import time

def search_open_access_fulltext(query, max_count=5, save_dir='epmc_articles'):
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)

    print(f"🔍 开始搜索关键词: {query}，最多获取 {max_count} 篇文章...")

    # Europe PMC 查询 API
    search_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query + " OPEN_ACCESS:Y",
        "format": "json",
        "pageSize": max_count
    }

    res = requests.get(search_url, params=params)
    results = res.json()["resultList"]["result"]

    for i, paper in enumerate(results):
        title = paper.get("title", "No Title")
        pmcid = paper.get("pmcid", None)
        if not pmcid:
            print(f"[{i+1}]  无 PMCID，跳过：{title}")
            continue

        print(f"[{i+1}] 📖 正在抓取：{title}")
        fulltext_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
        r = requests.get(fulltext_url)
        if r.status_code != 200:
            print(f"获取全文失败：{pmcid}")
            continue

        try:
            root = ET.fromstring(r.text)
            body = root.find(".//body")
            if body is not None:
                # 提取正文纯文本
                text_content = ''.join(body.itertext())
                # 简化文件名
                safe_title = ''.join(c for c in title if c.isalnum() or c in " _-")[:50]
                filename = os.path.join(save_dir, f"{safe_title}.txt")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                print(f"   已保存为：{filename}")
            else:
                print("   没有正文部分")
        except Exception as e:
            print(f" 解析失败：{e}")

        time.sleep(1)  # 避免请求过快被限制

    print("\n 文献抓取完成！")

# 调用，前面是关键词，后面是抓取文献数量
search_open_access_fulltext("bioinformatics cancer", max_count=5)
