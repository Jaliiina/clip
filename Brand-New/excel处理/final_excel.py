'''
最后删除不存在的图片名称，将更新后的数据保存到新的 Excel 文件中。
'''

import pandas as pd
import os

# 定义文件夹路径
base_folder_progressing = r"D:\多模态\图文对\保留\中文\人工智能\图文对"
base_folder_information = r"D:\多模态\人工智能\图文对\CNKI\18.01~24.10（中文100字符以上）\final"
output_folder = r"D:\多模态\图文对\保留\中文\人工智能\图文对"

# 获取所有文件夹和文件
progressing_folders = os.listdir(base_folder_progressing)
information_files = [f for f in os.listdir(base_folder_information) if f.endswith('.xlsx')]

# 定义处理函数
def process_file(input_file, images_folder, output_file):
    # 读取 Excel 文件
    df = pd.read_excel(input_file)

    # 获取指定文件夹中的所有 .jpg 文件名称
    jpg_files = {f for f in os.listdir(images_folder) if f.endswith('.jpg')}

    # 定义一个函数来处理第三列的图片名称
    def process_image_names(image_names):
        # 如果不是字符串，则返回空字符串
        if not isinstance(image_names, str):
            return ''
        # 分割图片名称（用逗号分隔）
        names = [name.strip() for name in image_names.split(',')]
        # 保留存在的文件名称
        existing_names = [name for name in names if name in jpg_files]
        # 返回有效的文件名称列表
        return ', '.join(existing_names)

    # 处理第三列
    df['图片名称'] = df['图片名称'].apply(process_image_names)

    # 删除所有图片名称均不存在的行
    df = df[df['图片名称'].str.strip() != '']

    # 将处理后的数据保存到新的 Excel 文件
    df.to_excel(output_file, index=False)

    print(f"处理完成，输出结果已保存到: {output_file}")

# 批处理每个文件
for info_file in information_files:
    # 构建文件路径
    input_file = os.path.join(base_folder_information, info_file)
    folder_name = os.path.splitext(info_file)[0] + '_data'
    images_folder = os.path.join(base_folder_progressing, folder_name)
    
    # 检查文件夹是否存在
    if not os.path.exists(images_folder):
        print(f"警告：文件夹 {images_folder} 不存在，跳过文件 {info_file}")
        continue
    
    # 构建输出文件路径
    output_file = os.path.join(output_folder, info_file)
    
    # 处理文件
    process_file(input_file, images_folder, output_file)