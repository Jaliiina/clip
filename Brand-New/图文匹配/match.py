'''
中文论文中进行图文配对，将图片与文字内容对应起来。
'''

import os  
import re  

def extract_text_from_markdown(markdown_filename):  
    """从 Markdown 文件中提取文本内容，与图片关联"""  
    print(markdown_filename)
    with open(markdown_filename, 'r', encoding='utf-8') as file:  
        content = file.read()  

    # 查找所有图片标签  
    img_pattern = r'!\[\]\((.*?)\)'  
    images = re.findall(img_pattern, content)  

    text_mapping = {}  

    # 按行分割内容，这样便于索引和检索上下行  
    lines = content.splitlines()  

    # 遍历每一张图片，进行二次检索  
    for img in images:  
        img_name = os.path.basename(img)  # 获取图片名称  

        # 获取图片出现的位置  
        img_position = content.find(img)  
        
        # 找到对应的行数  
        line_index = content[:img_position].count('\n')  # 计算图片前面有多少行  
        
        # 定义要检索的上下行数  
        upper_index = max(0, line_index - 2)  # 上一行  
        lower_index = min(len(lines) - 1, line_index + 2)  # 下一行  
        
        # 获取上下两行文本  
        context_lines = lines[upper_index: lower_index + 1]  
        context_text = ' '.join(context_lines).strip()  # 合并上下行文本  

        # 匹配下方的图  
        # number_pattern = r"(图|表)\s*(\d+)"  
        number_pattern = r"(图)\s*(\d+)"  
        
        # 查看前面最近的"图1"  
        numbers = re.findall(number_pattern, context_text)  
        if numbers:  
            last_section = numbers[-1]  
            section_name = f"{last_section[0]}{last_section[-1]}"  # 形式为“图1” 
            # print(last_section[0],last_section[-1])
            # 进行检索，抓取该图之前的所有内容  
            text_pattern = rf'(.*?{re.escape(last_section[0])}\s*{last_section[-1]}.*?。)'  
            text_matches = re.findall(text_pattern, content)  # 使用 findall 找到所有匹配  

            # 保存找到的所有文本内容  
            if text_matches:  
                text_mapping[img_name] = ' '.join(match.strip() for match in text_matches if match).strip()  

    return text_mapping  

def save_text_files(text_mapping, images_folder):  
    """将文本内容保存为 TXT 文件"""  
    for img_name, text in text_mapping.items():  
        if text:  
            # 使用 img_name 的基础名称作为 TXT 文件名称  
            base_name = os.path.splitext(img_name)[0]  # 去掉扩展名  
            txt_filename = os.path.join(images_folder, f"{base_name}.txt")  # 修正为正确的扩展名  
            with open(txt_filename, 'w', encoding='utf-8') as txt_file:  
                txt_file.write(text)  

def process_folders(input_folder):  
    """主处理函数，遍历输入文件夹并处理每个子文件夹"""  
    for root, dirs, files in os.walk(input_folder):  
        images_folder = os.path.join(root, 'images')  # 设定 images 文件夹地址  
        
        # 只处理含有 'images' 文件夹的路径  
        if 'images' in dirs:  
            # 查找 Markdown 文件  
            for file in files:  
                if file.endswith('.md'):  
                    markdown_file = os.path.join(root, file)  
                    text_mapping = extract_text_from_markdown(markdown_file)  
                    save_text_files(text_mapping, images_folder)  

if __name__ == "__main__":  
    input_folder = r"D:\多模态\机器视觉\CNKI-progressed"  # 指定输入文件夹  
    process_folders(input_folder)