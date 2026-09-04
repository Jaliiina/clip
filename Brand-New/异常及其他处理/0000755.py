'''
解析文件夹偶尔会出错，将错误文件删除。
'''
import os
import shutil

def delete_files(directory):
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name == '0000755.txt':
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except PermissionError as e:
                    print(f"Permission denied: {file_path} - {e}")
        for name in dirs:
            if name == '0000755':
                folder_path = os.path.join(root, name)
                try:
                    shutil.rmtree(folder_path)
                    print(f"Deleted folder: {folder_path}")
                except PermissionError as e:
                    print(f"Permission denied: {folder_path} - {e}")

# 替换为你的目录路径
directory_path = r"D:\多模态\机器视觉\CNKI-progressed"
delete_files(directory_path)