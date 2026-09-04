'''
将文件夹名称重新命名
'''
import os

def rename_files_and_folders(root_path):
    # 初始化计数器
    counter = 1
    
    # 遍历根目录下的所有子目录
    for folder_name in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder_name)
        
        # 检查是否是文件夹
        if os.path.isdir(folder_path):
            # 获取当前计数值作为新文件夹名称
            new_folder_name = str(counter)
            
            # 重命名文件夹
            os.rename(folder_path, os.path.join(root_path, new_folder_name))
            new_folder_path = os.path.join(root_path, new_folder_name)
            
            # 遍历新文件夹中的所有子目录和文件
            for subfolder_name in os.listdir(new_folder_path):
                subfolder_path = os.path.join(new_folder_path, subfolder_name)
                
                # 检查是否是文件夹
                if os.path.isdir(subfolder_path):
                    # 遍历子文件夹中的所有文件
                    for file_name in os.listdir(subfolder_path):
                        file_path = os.path.join(subfolder_path, file_name)
                        
                        # 检查文件名是否与原文件夹名称相同（包括.md文件）
                        if file_name.startswith(folder_name) and file_name.endswith('.md'):
                            # 构造新的文件名
                            new_file_name = f"{new_folder_name}.md"
                            
                            # 重命名文件
                            os.rename(file_path, os.path.join(subfolder_path, new_file_name))
            
            # 计数器加一
            counter += 1

# 指定路径
root_directory = r"D:\多模态\人工智能\CNKI-progressed\CCFA_data\root\autodl-tmp\data"

# 调用函数
rename_files_and_folders(root_directory)






