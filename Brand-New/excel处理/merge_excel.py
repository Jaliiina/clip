'''
合并CNKI的题录信息，并保存为excel文件。
'''
import os
import pandas as pd
from bs4 import BeautifulSoup

def html_to_excel(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    if not tables:
        return None
    df_list = []
    for table in tables:
        rows = table.find_all('tr')
        if not rows:
            continue
        header = [th.text.strip() for th in rows[0].find_all('th')]
        if not header:
            # 如果没有<th>标签，尝试使用<td>标签作为header
            header = [td.text.strip() for td in rows[0].find_all('td')]
        data = []
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            data.append(cols)
        # 检查header是否为空
        if header:
            df = pd.DataFrame(data, columns=header)
            df_list.append(df)
        else:
            print(f"No header found in table, skipping table...")
    return pd.concat(df_list, ignore_index=True) if df_list else None
def merge_excel_in_folder(folder_path):
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            excel_files = []
            for file in os.listdir(subfolder_path):
                if file.endswith('.xls'):
                    xls_file_path = os.path.join(subfolder_path, file)
                    with open(xls_file_path, 'r', encoding='utf-8') as file:
                        html_content = file.read()
                        df = html_to_excel(html_content)
                        if df is not None:
                            excel_files.append(df)
            
            if excel_files:
                merged_df = pd.concat(excel_files, ignore_index=True)
                output_file_path = os.path.join(folder_path, f'{subfolder}.xlsx')
                merged_df.to_excel(output_file_path, index=False)
                print(f'Merged file saved as {output_file_path}')

# Replace 'your_main_folder_path' with the path to your main folder
main_folder_path = r'D:\AI科技类内容图文匹配\题录'
merge_excel_in_folder(main_folder_path)