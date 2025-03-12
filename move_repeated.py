import os
import shutil
from collections import defaultdict

def read_file_content(file_path):
    """读取文本文件的内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def find_duplicates(input_dir, output_dir):
    """查找重复的.txt文件，并移动相应的.jpg和.txt文件到输出目录"""
    # 存储文本内容及其对应的文件路径
    content_dict = defaultdict(list)
    
    # 遍历输入目录下的所有子目录
    for subdir in os.scandir(input_dir):
        if subdir.is_dir():
            # 对于每个子目录，遍历其中的所有文件
            for file in os.scandir(subdir.path):
                if file.name.endswith('.txt'):
                    content = read_file_content(file.path)
                    # 将内容相同的文件路径添加到列表中
                    content_dict[content].append((subdir.name, file.name[:-4]))
    
    # 根据找到的重复项进行操作
    for duplicates in content_dict.values():
        if len(duplicates) > 1:
            for (subdir_name, base_name) in duplicates:
                src_jpg = os.path.join(input_dir, subdir_name, f"{base_name}.jpg")
                src_txt = os.path.join(input_dir, subdir_name, f"{base_name}.txt")
                
                dst_subdir = os.path.join(output_dir, subdir_name)
                if not os.path.exists(dst_subdir):
                    os.makedirs(dst_subdir)
                
                shutil.move(src_jpg, os.path.join(dst_subdir, f"{base_name}.jpg"))
                shutil.move(src_txt, os.path.join(dst_subdir, f"{base_name}.txt"))

def group_files_by_content(source_folder):
    # 创建一个字典来存储内容相同的所有文件路径
    content_to_files = {}

    # 遍历源文件夹中的所有文件
    for filename in os.listdir(source_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(source_folder, filename)
            with open(file_path, 'r') as file:
                content = read_file_content(file_path)
                
                # 如果内容不在字典中，则创建一个新的键值对
                if content not in content_to_files:
                    content_to_files[content] = []
                    
                # 将文件路径添加到对应的内容列表中
                content_to_files[content].append(filename)

    # 按顺序编号创建新文件夹并将文件移动进去
    folder_index = 1
    for content, files in content_to_files.items():
        new_folder_name = f"group_{folder_index}"
        new_folder_path = os.path.join(source_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)
        
        for file in files:
            base_filename = os.path.splitext(file)[0]
            
            # 移动.txt文件
            txt_file_path = os.path.join(source_folder, file)
            shutil.move(txt_file_path, new_folder_path)
            
            # 移动.jpg文件（如果有）
            jpg_file_path = os.path.join(source_folder, f"{base_filename}.jpg")
            if os.path.exists(jpg_file_path):
                shutil.move(jpg_file_path, new_folder_path)
        
        folder_index += 1

def same_content(dir):
    """主处理函数，遍历输入文件夹并处理每个子文件夹"""
    for folder in os.listdir(dir):
        folder_path = os.path.join(dir, folder)
        if os.path.isdir(folder_path):  # 确保是文件夹
            group_files_by_content(folder_path)
# 设置输入和输出目录
input_directory = r"D:\多模态\自定义\图文对\origin"
output_directory = r"D:\多模态\自定义\图文对\repeated"

find_duplicates(input_directory, output_directory)
same_content(output_directory)