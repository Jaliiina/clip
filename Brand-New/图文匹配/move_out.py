'''
将图文对移动到上一级文件夹，并删除空的子文件夹。
'''
import os
import shutil

def move_files_and_delete_subfolders(root_folder):
    # 遍历根文件夹及其所有子文件夹
    for root, dirs, _ in os.walk(root_folder, topdown=False):
        for dir_name in dirs:
            # 获取子文件夹的完整路径
            subfolder_path = os.path.join(root, dir_name)
            # 获取子文件夹内的所有文件
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith('.jpg') or file_name.endswith('.txt'):
                    # 构建完整的文件路径
                    file_path = os.path.join(subfolder_path, file_name)
                    # 移动文件到上一级文件夹（即月份分类文件夹）
                    target_path = os.path.dirname(subfolder_path)
                    try:
                        if os.path.exists(os.path.join(target_path, file_name)):
                            os.remove(os.path.join(target_path, file_name))
                        shutil.move(file_path, target_path)
                    except shutil.Error as e:
                        print(f"Error: {file_path} -> {target_path}: {e.strerror}")
            # 删除空的子文件夹
            try:
                os.rmdir(subfolder_path)
            except OSError as e:
                print(f"Error: {subfolder_path} - {e.strerror}")

def process_folders(input_folder):
    """主处理函数，遍历输入文件夹并处理每个子文件夹"""
    for folder in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder)
        if os.path.isdir(folder_path):  # 确保是文件夹
            move_files_and_delete_subfolders(folder_path)

if __name__ == '__main__':
    root_folder = r'D:\多模态\机器视觉\CNKI-progressing'
    process_folders(root_folder)