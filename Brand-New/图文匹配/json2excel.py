import os
import pandas as pd
import json

def process_folder(root_folder):
    # 遍历根文件夹下的所有子文件夹
    for foldername, subfolders, filenames in os.walk(root_folder):
        data = []
        for filename in filenames:
            if filename.endswith('.json'):
                file_path = os.path.join(foldername, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = json.load(file)
                    if isinstance(content, list) and len(content) > 0:
                        item = content[0]
                        if 'type' in item:
                            id_name = os.path.splitext(filename)[0]
                            data.append({'id': id_name, 'type': item['type']})
        
        if data:
            df = pd.DataFrame(data)
            excel_file_path = os.path.join(foldername, f'{os.path.basename(foldername)}.xlsx')
            df.to_excel(excel_file_path, index=False)

# 使用示例：指定根文件夹路径
root_folder_path = r'D:\多模态\图文对\人工智能\origin'
process_folder(root_folder_path)



