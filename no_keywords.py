'''
移动没有图表编号的pdf文件到指定文件夹
'''
import os
import re
import fitz  # PyMuPDF
import shutil

def move_pdfs_without_figure_numbers(source_folder, target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 匹配字样
    figure_number_pattern = re.compile(r'(图)\s*(\d+)')

    # 遍历源文件夹中的所有 PDF 文件
    for filename in os.listdir(source_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(source_folder, filename)

            # 打开 PDF 文件
            with fitz.open(pdf_path) as pdf:
                # 检查每一页是否包含图表编号
                contains_figure_number = False
                for page_num in range(pdf.page_count):
                    page = pdf[page_num]
                    text = page.get_text()
                    # 检查文本中是否包含图表编号
                    if figure_number_pattern.search(text):
                        contains_figure_number = True
                        break

            # 如果 PDF 中不包含图表编号
            if not contains_figure_number:
                # 将 PDF 文件移动到目标文件夹
                target_path = os.path.join(target_folder, filename)
                shutil.move(pdf_path, target_path)
                print(f"Moved '{filename}' to '{target_folder}'.")
            else:
                print(f"'{filename}' contains figure numbers and will not be moved.")

# 使用示例
source_folder = r"D:\多模态\人工智能\CNKI-pdf\24.10" 
target_folder = r"D:\多模态\人工智能\CNKI-deleted\24.10"
move_pdfs_without_figure_numbers(source_folder, target_folder)
