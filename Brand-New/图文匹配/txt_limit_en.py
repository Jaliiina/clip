'''
对文档英文字符数进行筛选，小于字符的文档和其对应的图片一起移动到指定文件夹。
'''
import os
import shutil

def is_english_char(char):
    """判断字符是否为英文字符"""
    if char.isalpha() and char.lower() not in '0123456789':
        return True
    return False

def count_english_chars(text):
    """统计文本中英文字符的数量"""
    return sum(is_english_char(char) for char in text)

def move_files(src_folder, dest_folder, min_chars):
    # 确保目标文件夹存在
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # 递归遍历源文件夹中的所有文件
    for root, dirs, files in os.walk(src_folder):
        for filename in files:
            if filename.endswith(".txt"):
                # 构造完整的文件路径
                txt_path = os.path.join(root, filename)
                # 读取文件内容
                with open(txt_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # 检查英文字符数量
                if count_english_chars(content) < min_chars:
                    # 构造同名的jpg文件路径
                    jpg_filename = filename[:-4] + ".jpg"
                    jpg_path = os.path.join(root, jpg_filename)
                    txt_filename = filename[:-4] + ".txt"
                    # 检查jpg文件是否存在
                    if os.path.exists(jpg_path):
                        try:
                            if os.path.exists(os.path.join(dest_folder, jpg_filename)):
                                os.remove(os.path.join(dest_folder, jpg_filename))
                                os.remove(os.path.join(dest_folder, txt_filename))
                            # 移动txt文件
                            shutil.move(txt_path, dest_folder)
                            # 移动jpg文件
                            shutil.move(jpg_path, dest_folder)
                        except Exception as e:
                            print("Error moving files:", e)
                        # print(f"Moved {txt_path} and {jpg_path} to {dest_folder}")

# 指定源文件夹和目标文件夹
source_folder = 'D:/多模态/人工智能/CNKI-progressing'
destination_folder = 'D:/多模态/人工智能/temp'
min_english_chars = 250  # 设置英文字符的最小数量

# 调用函数
move_files(source_folder, destination_folder, min_english_chars)