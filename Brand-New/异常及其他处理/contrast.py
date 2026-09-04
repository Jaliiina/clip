import os
import shutil

def compare_and_delete_files(dir_a, dir_b):
    # 遍历dir_a中的所有文件和子目录
    for root, dirs, files in os.walk(dir_a):
        # 计算相对路径
        relative_path = os.path.relpath(root, dir_a)
        target_dir = os.path.join(dir_b, relative_path)

        # 检查target_dir是否存在
        if not os.path.exists(target_dir):
            continue
        
        # 对比文件
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)
            
            if os.path.exists(target_file):
                print(f"Deleting {source_file} because it exists in {target_file}")
                os.remove(source_file)

# 示例调用
dir_a = r'D:\多模态\图文对\temp\origin'
dir_b = r'D:\多模态\图文对\temp\repeated'
compare_and_delete_files(dir_a, dir_b)



