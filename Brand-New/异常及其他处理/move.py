'''
将文件从子文件夹移至父级文件夹下
'''
import os  
import shutil  

def move_files_to_parent_folder(folder_path):  
    # 确保提供的路径是一个有效的文件夹  
    if not os.path.isdir(folder_path):  
        print(f"{folder_path} 不是一个有效的文件夹路径.")  
        return  

    # 遍历文件夹下的所有内容  
    for root, dirs, files in os.walk(folder_path):  
        # 排除当前文件夹  
        if root == folder_path:  
            continue  
        
        for file in files:  
            source_file = os.path.join(root, file)  
            destination_file = os.path.join(folder_path, file)  

            # 如果目标文件已存在，直接覆盖  
            if os.path.exists(destination_file):  
                print(f"覆盖文件: {destination_file}")  

            # 移动文件到目标文件夹  
            shutil.move(source_file, destination_file)  
            print(f"已移动: {source_file} 到 {folder_path}")  

    print("所有文件已移动。")  

# 使用示例  
folder_path = r'D:\多模态\图文对\CCFA\剔除\CCFA'    # 替换为你的目标文件夹路径  
move_files_to_parent_folder(folder_path)
