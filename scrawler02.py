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


'''
将表格放在代码保存和运行的路径内，将wb变量内的'n0606.xlsx'改为自己的excel文件名,
最后下载的论文在该路径下新建的papers文件夹内
'''
wb = openpyxl.load_workbook('D:\move11\doi2.xlsx')
# doi在sheet1中
sheet1 = wb.get_sheet_by_name('Sheet1')
# 读取第A列

'''
修改代码内，excel中DOI所在列，我的在BC，所以col_range变量后面的字符改为了‘BC’
'''
col_range = sheet1['A']
# 读取其中的第几行：row_range = sheet1[2:6]
fails = []

# 以下代码加入了我找的其他SCI-hub网址，不需要可以删除一些
for col in col_range:  # 打印BC两列单元格中的值内容
    doi = col.value
    print(doi)
    if __name__ == '__main__':
        sci_Hub_Url = "https://sci-hub.shop/"
        paper_url = sci_Hub_Url + doi
        print(paper_url)
        nmm = 0
        try:
            getPaperPdf(paper_url)  # 通过文献的url下载pdf
            continue
        except Exception:
            print("Failed to get pdf 1")


# 获取下载失败的doi
print(fails)
