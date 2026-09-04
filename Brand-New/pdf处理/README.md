# MinerU
代码通过调用API方式使用MinerU解析文件：
·支持.pdf、.doc、.docx、.ppt、.pptx、.png、.jpg、.jpeg多种格式；
·解析有pipeline及vlm两种方式，前者速度快效果略差，后者速度慢效果略好，可按需选择方式；
·解析过程为提交请求及下载解压两个过程，可指定选择下载位置及解压位置；

API已提供，所有 API Tokens 有效期为 14 天，请在过期前更新 API Tokens。
如需更新API，请到官网注册在API下填写请求，大约十几分钟通过审核，即可创建API Token。
官网也提供客户端版本，可按需使用。
API额度：每日10000份文件，每日优先解析额度2000页。
官方网站：
https://mineru.net/

# 文件结构
test.py 示例调用使用代码
MinerU文件夹下存放封装代码供其他程序调用
mineru.py 请求解析代码
download 下载解析结果压缩包并解压代码
mineru_api 请求并下载解压代码
.env 存放API Token，在此修改

建议Python版本：3.10-3.13