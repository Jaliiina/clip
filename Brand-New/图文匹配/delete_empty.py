'''
删除空文件夹。
'''
import os

def remove_empty_folders(path):
    # 从底层文件夹开始向上遍历
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            if not os.listdir(folder_path):  # 如果文件夹为空
                os.rmdir(folder_path)  # 删除空文件夹
                print(f"Removed empty folder: {folder_path}")

# 指定源文件夹和目标文件夹
source_folder = r'D:\中国标准化研究院\文物保护_markdown'

# 删除空文件夹
remove_empty_folders(source_folder)
