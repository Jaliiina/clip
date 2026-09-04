'''
根据中图分类号映射表，将CLC-中图分类号列中的分类号替换为对应的分类名称。
'''
import pandas as pd
import os
import re

# 读取中图分类号映射表
mapping_df = pd.read_excel(r"D:\\多模态\\人工智能\\中图分类号.xlsx", header=None)
mapping_dict = dict(zip(mapping_df[0], mapping_df[1]))

# 指定文件夹路径
folder_path = r"D:\多模态\机器视觉\CNKI-excel\汇总"
output_path = r"D:\多模态\机器视觉\CNKI-excel\添加分类"
# 遍历文件夹中的所有.xlsx文件
for file_name in os.listdir(folder_path):
    if file_name.endswith(".xlsx") and file_name != "中图分类号.xlsx":
        file_path = os.path.join(folder_path, file_name)
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 处理CLC-中图分类号列，添加分类名称列
        def get_category_names(clc_code):
            # 根据分类号获取名称
            names = set()
            # 使用正则表达式匹配分类号中的字母部分
            for code in clc_code.split(';'):
                # 匹配分类号中的字母部分
                match = re.match(r'([A-Z]+)', code.strip())
                if match:
                    category_code = match.group(1)
                    if category_code in mapping_dict:
                        names.add(mapping_dict[category_code])
            return '; '.join(names)
        
        # 应用函数到CLC-中图分类号列
        df['分类名称'] = df['CLC-中图分类号'].apply(get_category_names)
        
        # 另存为新文件
        new_file_path = os.path.join(output_path, f"{os.path.splitext(file_name)[0]}.xlsx")
        df.to_excel(new_file_path, index=False)
        print(f"已成功处理并保存文件：{new_file_path}")

print("处理完成。")