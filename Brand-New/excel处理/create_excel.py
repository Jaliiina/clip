'''
创建Excel文件，用于存储标题、作者和图片名称。
'''
import os
import pandas as pd

def process_folder(folder_path, output_folder):
    """处理单个文件夹，生成对应的Excel文件"""
    # 初始化一个空的DataFrame
    df = pd.DataFrame(columns=['标题', '作者', '图片名称'])

    # 遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            if dir.endswith(" (1)") or dir.endswith(" (2)") or dir.endswith(" (3)"):
                dir = dir[:-4]
            last_underscore_index = dir.rfind('_')  # 找到最后一个“_”的位置
            
            if len(dir) - 6 < last_underscore_index < len(dir):  
                title = dir[:last_underscore_index]  # 标题是“_”之前的部分  
                author = dir[last_underscore_index + 1:]  # 作者是“_”之后的部分  
            elif last_underscore_index != -1 and last_underscore_index > 0 and dir[last_underscore_index - 1] != '_':  
                title = dir[:last_underscore_index]  # 标题是“_”之前的部分  
                author = dir[last_underscore_index + 1:]  # 作者是“_”之后的部分  
            else:  # 如果不符合条件，则只有标题  
                title = dir  
                author = ''  
            
            # 构建“auto”文件夹的路径
            images_path = os.path.join(root, dir)
            if os.path.exists(images_path):  # 如果图片文件夹存在
                image_names = [file for file in os.listdir(images_path) if file.endswith(".jpg")]
                # 将所有图片名称合并为一个字符串
                images_str = ', '.join(image_names)
                # 添加到DataFrame
                df = df._append({'标题': title, '作者': author, '图片名称': images_str}, ignore_index=True)

    # 生成Excel文件名
    excel_name = os.path.basename(folder_path) + '.xlsx'
    excel_path = os.path.join(output_folder, excel_name)
    
    # 写入Excel文件
    df.to_excel(excel_path, index=False, engine='openpyxl')

    print(f"Excel文件已生成在：{excel_path}")

def process_folders(input_folder):
    """主处理函数，遍历输入文件夹并处理每个子文件夹"""
    for folder in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder)
        if os.path.isdir(folder_path):  # 确保是文件夹
            process_folder(folder_path)

if __name__ == "__main__":
    input_folder = r'D:\多模态\机器视觉\CNKI-progressing'  # 指定输入文件夹
    output_folder = r'D:\\多模态\\机器视觉\\CNKI-excel\\图文对信息版'  # 指定输出文件夹
    process_folders(input_folder, output_folder)