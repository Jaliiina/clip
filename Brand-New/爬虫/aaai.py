import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from IPython.display import Audio
sound_file='hey.m4a'

# 设定要保存论文的文件夹 (保存至 D 盘)
save_folder = r"D:\AAAI_papers"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# 目标网址列表
urls = [



       
       'https://ojs.aaai.org/index.php/SOCS/issue/view/431'

]

# 请求头设置
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 遍历每个网址
for url in urls:
    print(f"正在处理网址: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 确保响应成功
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        continue

    # 解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有 PDF 的链接
    pdf_links = soup.find_all('a', class_='obj_galley_link pdf')
    print(f"找到 {len(pdf_links)} 个 PDF 链接")  # 调试信息

    if len(pdf_links) == 0:
        print("未找到任何 PDF 链接，跳过此网址。")
        continue

    # 下载每个 PDF 文件
    for link in pdf_links:
        pdf_url = urljoin(url, link['href'])
        print(f"发现 PDF 链接: {pdf_url}")  # 输出 PDF 链接用于调试

        # 获取文件名
        file_name = pdf_url.split("/")[-1] + ".pdf"  # 修改文件名提取方式
        print(f"提取的文件名为: {file_name}")  # 调试信息
        file_path = os.path.join(save_folder, file_name)

        if os.path.exists(file_path):
            print(f"{file_name} 已经存在，跳过下载。")
            print(f"文件路径: {file_path} 是否存在: {os.path.exists(file_path)}")  # 调试信息
            continue

        print(f"正在下载 {file_name}...")
        try:
            pdf_response = requests.get(pdf_url, headers=headers, stream=True)
            pdf_response.raise_for_status()  # 确保下载成功

            # 保存 PDF 文件
            with open(file_path, 'wb') as f:
                for chunk in pdf_response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # 检查文件是否为空
            if os.path.getsize(file_path) == 0:
                print(f"{file_name} 下载失败，文件为空，已删除。")
                os.remove(file_path)
            else:
                print(f"{file_name} 下载完成并保存至 {file_path}")
                print("继续处理下一个链接...")  # 调试信息

        except requests.exceptions.RequestException as e:
            print(f"下载 {file_name} 时出错: {e}")

        # 避免过于频繁的请求，加入延迟
        time.sleep(2)

print("所有 PDF 文件下载完毕")
notify=Audio(sound_file,autoplay=True)
notify
