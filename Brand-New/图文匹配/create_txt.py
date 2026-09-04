'''
为每个图片创建一个空白的txt文件
'''
import os

def create_blank_txt_for_images(root_dir):
    # 遍历root_dir下的所有文件夹
    for subdir, dirs, files in os.walk(root_dir):
        # 检查是否存在auto文件夹
        for dir_name in dirs:
            if dir_name == 'auto':
                auto_dir = os.path.join(subdir, dir_name)
                # 检查是否存在images文件夹
                if 'images' in os.listdir(auto_dir):
                    images_dir = os.path.join(auto_dir, 'images')
                    # 遍历images文件夹下的所有图片
                    for image in os.listdir(images_dir):
                        # 获取图片的完整路径
                        image_path = os.path.join(images_dir, image)
                        # 获取图片的文件名（不包括扩展名）
                        image_name = os.path.splitext(image)[0]
                        # 创建与图片同名的txt文件
                        txt_path = os.path.join(images_dir, image_name + '.txt')
                        # 如果txt文件不存在，则创建一个空白的txt文件
                        if not os.path.exists(txt_path):
                            try:
                                open(txt_path, 'x').close()
                            except FileExistsError:
                                print("File already exists")
                            with open(txt_path, 'w') as f:
                                pass  # 创建空白文件

# 调用函数，传入你的根目录路径
root_dir = r"D:\多模态\机器视觉\CNKI-progressed"
create_blank_txt_for_images(root_dir)