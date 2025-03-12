'''
解压pdf文件可能会产生一些额外的字符，删除这些额外的字符，以便于后续的处理。
'''
import os
import re

def clean_pdf_filenames(root_dir):
    # 遍历指定目录及其子目录
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            # 检查文件是否以.pdf结尾，并且文件名中有额外的字符
            if re.search(r'\.pdf\d+$', filename):
                # 构建完整的文件路径
                file_path = os.path.join(dirpath, filename)
                # 使用正则表达式替换多余的字符
                new_filename = re.sub(r'\.pdf\d+$', '.pdf', filename)
                new_file_path = os.path.join(dirpath, new_filename)
                # 重命名文件
                os.rename(file_path, new_file_path)
                print(f'Renamed "{file_path}" to "{new_file_path}"')

# 指定的目录
root_directory = 'D:\\多模态\\人工智能\\CNKI-pdf'
clean_pdf_filenames(root_directory)