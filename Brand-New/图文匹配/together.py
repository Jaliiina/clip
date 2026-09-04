'''
将所有图文对放在一个文件夹下，方便筛选。
'''
import os  
import shutil  

def copy_images_to_target(root_dir, target_base_dir):  
    # 遍历根目录下的所有文件夹  
    for dir_name in os.listdir(root_dir):  
        dir_path = os.path.join(root_dir, dir_name)  

        # 确保是文件夹  
        if os.path.isdir(dir_path):  
            # 根据实际结构构建图文对路径  
            target_images_path = os.path.join(dir_path, 'root', 'autodl-tmp', 'data')  
            print(f"Checking target images path: {target_images_path}")  # 调试打印  

            # 遍历 data 目录下的每个项目  
            for item in os.listdir(target_images_path):  
                item_path = os.path.join(target_images_path, item)  

                # 确保是文件夹并且存在 auto/images 子目录  
                if os.path.isdir(item_path):  
                    images_path = os.path.join(item_path, 'auto', 'images')  
                    
                    if os.path.exists(images_path):  
                        # 创建目标文件夹  
                        target_dir = os.path.join(target_base_dir, dir_name, item)  
                        os.makedirs(target_dir, exist_ok=True)  

                        # 复制 images 目录下的所有文件  
                        for file in os.listdir(images_path):  
                            src_file = os.path.join(images_path, file)  
                            dst_file = os.path.join(target_dir, file)  

                            # 复制文件  
                            shutil.copy2(src_file, dst_file)  
                            # print(f"Copied {src_file} to {dst_file}")  
                    else:  
                        print(f"No images found in: {images_path}")  # 调试打印  

# 调用函数  
root_directory = r"D:\多模态\机器视觉\CNKI-progressed"  # 替换为你的根目录路径  
target_directory = r"D:\多模态\机器视觉\CNKI-progressing"  # 替换为你的目标文件夹路径  
copy_images_to_target(root_directory, target_directory)