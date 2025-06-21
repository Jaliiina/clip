import feedparser
import requests
import os
import time

def download_arxiv_papers(query="bioinformatics", max_results=5, save_dir="arxiv_pdfs"):
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)

    # 构造搜索 URL（ 基于 RSS）
    feed_url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"

    print(f" 正在搜索关键词：{query}（共 {max_results} 篇）")
    feed = feedparser.parse(feed_url)

    for i, entry in enumerate(feed.entries):
        title = entry.title.strip().replace('\n', ' ')
        print(f"\n[{i+1}] 📄 {title}")

        # PDF 下载链接
        pdf_url = entry.id.replace('abs', 'pdf') + ".pdf"

        try:
            # 构造保存路径
            safe_title = ''.join(c for c in title if c.isalnum() or c in " _-")[:50]
            filename = os.path.join(save_dir, f"{safe_title}.pdf")

            # 下载 PDF
            response = requests.get(pdf_url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f" 下载成功：{filename}")
            else:
                print(f" 下载失败，状态码：{response.status_code}")

        except Exception as e:
            print(f" 出错：{e}")

        time.sleep(1)  # 避免请求过快

    print(f" 已完成下载，文件保存在文件夹：{save_dir}/")

# 改query里的关键词就好
download_arxiv_papers(query="bioinformatics", max_results=10)
