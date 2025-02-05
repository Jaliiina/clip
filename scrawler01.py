import requests
import re
import os
import urllib.request
import openpyxl

# headers 保持与服务器的会话连接
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
}


def getPaperPdf(url):
    pattern = '/.*?\.pdf'
    content = requests.get(url, headers=headers)
    download_url = re.findall(pattern, content.text)
    # print(download_url)
    download_url[1] = "https:" + download_url[1]
    print(download_url[1])
    path = r"D:\move11\sci"
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)

    # 使用 urllib.request 来包装请求
    req = urllib.request.Request(download_url[1], headers=headers)
    # 使用 urllib.request 模块中的 urlopen方法获取页面
    u = urllib.request.urlopen(req, timeout=5)

    file_name = download_url[1].split('/')[-2] + '%' + download_url[1].split('/')[-1]
    f = open(path + '/' + file_name, 'wb')

    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        f.write(buffer)
    f.close()
    print("Successful to download" + " " + file_name)


#读取存放doi的excel
wb = openpyxl.load_workbook('D:\move11\doi.xlsx')

sheet1 = wb.get_sheet_by_name('Sheet1')

col_range = sheet1['A']

fails = []

# 以下代码加入了我找的其他SCI-hub网址，不需要可以删除一些
for col in col_range:
    doi = col.value
    print(doi)
    if __name__ == '__main__':
        sci_Hub_Url = "https://sci-hub.ren/"
        paper_url = sci_Hub_Url + doi
        print(paper_url)
        nmm = 0
        try:
            getPaperPdf(paper_url)  # 通过文献的url下载pdf
            continue
        except Exception:
            nmm = 1
            print("Failed to get pdf 1")
        if nmm == 1:
            try:
                sci_Hub_Url_2 = "https://sci-hub.se/"
                paper_url_2 = sci_Hub_Url_2 + doi
                getPaperPdf(paper_url_2)

                continue
            except Exception:
                print("Failed to get pdf 2")
        if nmm == 1:
            try:
                sci_Hub_Url_3 = "https://sci-hub.st/"
                paper_url_3 = sci_Hub_Url_3 + doi
                getPaperPdf(paper_url_3)
                continue
            except Exception:
                print("Failed to get pdf 3")
        if nmm == 1:
            try:
                sci_Hub_Url_4 = "https://sci-hub.shop/"
                paper_url_4 = sci_Hub_Url_4 + doi
                getPaperPdf(paper_url_4)
                continue
            except Exception:
                print("Failed to get pdf 4")
        if nmm == 1:
            try:
                sci_Hub_Url_5 = "https://sci-hub.shop/"
                paper_url_5 = sci_Hub_Url_5 + doi
                getPaperPdf(paper_url_5)
                continue
            except Exception:
                print("Failed to get pdf 5")
        if nmm == 1:
            try:
                sci_Hub_Url_7 = "https://sci-hub.do/"
                paper_url_7 = sci_Hub_Url_7 + doi
                getPaperPdf(paper_url_7)
                continue
            except Exception:
                print("Failed to get pdf 7")
        if nmm == 1:
            try:
                sci_Hub_Url_6 = "https://libgen.ggfwzs.net/"
                paper_url_6 = sci_Hub_Url_6 + doi
                getPaperPdf(paper_url_6)
                continue
            except Exception:
                print("Failed to get pdf 6")
                fails.append(doi)

# 获取下载失败的doi
print(fails)
