'''
删除重复下载的pdf文件
'''
import os
import shutil

def move_pdf_files(src_folder, dest_folder, endings):
    # 确保目标文件夹存在
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # 遍历源文件夹
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            # 检查文件名是否以指定的结尾之一结束
            if any(file.endswith(ending) for ending in endings):
                # 构建完整的文件路径
                src_file_path = os.path.join(root, file)
                dest_file_path = os.path.join(dest_folder, file)
                
                # 移动文件
                shutil.move(src_file_path, dest_file_path)
                print(f"Moved: {src_file_path} to {dest_file_path}")

# 指定源文件夹和目标文件夹
source_folder = r'D:\多模态\人工智能\CNKI-deleted'
destination_folder = r'D:\多模态\人工智能\temp'

# 指定文件结尾
endings = ['(1).pdf', '(2).pdf', '(3).pdf', '(4).pdf', '(5).pdf', '(6).pdf',]

# 调用函数
move_pdf_files(source_folder, destination_folder, endings)