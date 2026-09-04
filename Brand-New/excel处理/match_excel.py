'''
匹配图文对与文章的信息，并将结果保存到新的excel文件中。
'''
import os
import pandas as pd
import re

def merge_excel_files(file_a, file_b, output_file):
    # 读取Excel文件A
    df_a = pd.read_excel(file_a)
    
    # 读取Excel文件B
    df_b = pd.read_excel(file_b)
    
    # 创建一个空的DataFrame来存储结果
    df_c = pd.DataFrame(columns=['标题', '作者', '图片名称', 'SrcDatabase-来源库', 'Title-题名', 'Author-作者', 'Organ-单位', 'Source-文献来源', 'Keyword-关键词', 'Summary-摘要', 'PubTime-发表时间', 'FirstDuty-第一责任人', 'Fund-基金', 'Year-年', 'Volume-卷', 'Period-期', 'PageCount-页码', 'CLC-中图分类号', 'ISSN-国际标准刊号', 'URL-网址', 'DOI-DOI', '分类名称'])
    
    # 定义一个函数来替换和转义特殊字符
    def replace_and_escape_special_chars(title):
        # 替换和转义特殊字符
        title = re.sub(r'[+]', r'\+', title)  # 转义"+"
        title = re.sub(r'[(]', r'$', title)  # 移除"( )"
        title = re.sub(r'[)]', r'$', title)  # 移除"( )"
        title = re.sub(r'_', r'[^_]+', title)  # 替换"_"为任意字符
        title = re.sub(r'\.{3,}', r'[^.]+', title)  # 替换"..."为任意字符
        return title
    
    # 遍历文件A中的每一行
    for index, row in df_a.iterrows():
        # 检查标题并替换特殊字符
        title_a = str(row['标题'])  # 确保是字符串类型
        title_a = replace_and_escape_special_chars(title_a)  # 替换和转义特殊字符
        
        # 确保作者是字符串类型，如果作者是空的，则设置为一个默认值，以便在比较时不会匹配任何内容
        author_a = str(row['作者']) if pd.notnull(row['作者']) else ''
        
        # 根据作者在B中进行匹配
        if author_a:
            matched_rows_by_author = df_b[df_b['FirstDuty-第一责任人'].str.contains(author_a, case=False, na=False)]
            # 如果匹配到的信息仅有一个，则进行添加
            if len(matched_rows_by_author) == 1:
                matched_rows = matched_rows_by_author
            else:
                # 如果信息不止一个，则根据标题进行进一步匹配
                matched_rows_by_title = matched_rows_by_author[matched_rows_by_author['Title-题名'].str.contains(title_a, case=False, na=False)]
                matched_rows = matched_rows_by_title
        else:
            # 如果作者为空，则仅根据标题进行匹配
            matched_rows = df_b[df_b['Title-题名'].str.contains(title_a, case=False, na=False)]
        
        # 如果找到匹配的行
        if not matched_rows.empty:
            # 将文件B中的所有列添加到文件A的对应行中
            for i, matched_row in matched_rows.iterrows():
                # 将A中的信息和B中的匹配信息合并
                merged_data = {
                    '标题': row['标题'],
                    '作者': row['作者'],
                    '图片名称': row['图片名称'],
                    **matched_row.to_dict()
                }
                df_c = pd.concat([df_c, pd.DataFrame([merged_data])], ignore_index=True)
        else:
            # 如果没有找到匹配的行，只添加A中的信息
            df_c = pd.concat([df_c, pd.DataFrame([{
                '标题': row['标题'],
                '作者': row['作者'],
                '图片名称': row['图片名称'],
                **{col: None for col in df_b.columns if col not in ['Title-题名', 'Author-作者']}
            }])], ignore_index=True)
    
    # 保存结果到新的Excel文件C
    df_c.to_excel(output_file, index=False)

def process_all_files(data_dir, info_dir, output_dir):
    data_files = [f for f in os.listdir(data_dir) if '_data.xlsx' in f]
    
    for data_file in data_files:
        base_name = data_file.split('_data')[0]
        corresponding_info_file = next((info_file for info_file in os.listdir(info_dir) if base_name in info_file), None)
        
        if corresponding_info_file:
            file_a_path = os.path.join(data_dir, data_file)
            file_b_path = os.path.join(info_dir, corresponding_info_file)
            output_file_path = os.path.join(output_dir, f"{base_name}.xlsx")
            
            print(f"Processing {file_a_path} with {file_b_path}")
            merge_excel_files(file_a_path, file_b_path, output_file_path)
        else:
            print(f"No corresponding info file found for {data_file}")

# 调用函数，传入数据文件夹路径、信息文件夹路径和输出文件夹路径
process_all_files(
    r'D:\多模态\机器视觉\CNKI-excel\图文对信息版',
    r'D:\多模态\机器视觉\CNKI-excel\添加分类',
    r'D:\多模态\机器视觉\CNKI-information'
)