import torch

import cn_clip.clip as clip
from PIL import Image, UnidentifiedImageError
from cn_clip.clip import load_from_name
import os
import re
import pandas as pd

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"

# 加载模型
model, preprocess = load_from_name("ViT-B-16", device=device, download_root='./')
model.eval()

# 加载Excel文件中的文章内容
excel_path = r"D:\move11\esult.xlsx"
df = pd.read_excel(excel_path)

# 创建保存配对结果的文件夹
output_folder = r"D:\move11\配对结果"
os.makedirs(output_folder, exist_ok=True)

# 迭代Excel中的每一行，处理文章和对应的图片
for index, row in df.iterrows():
    title = row['标题']  # 假设Excel第一列是标题，列名为 "标题"
    content = row['内容']  # 假设Excel第二列是文章内容，列名为 "文章内容"


    paragraphs = re.split(
        r'\s*#\s*|'
        r'\s*（[一二三四五六七八九十]+）\s*|'
        r'[一二三四五六七八九十]+、|'
        r'[0-9]+\.[0-9]+|'
        r'[0-9]+、|' 
        r'🍔|🍀|💯|🌈|🔥|💫',
        content
    )

    paragraphs = [para.strip() for para in paragraphs if para.strip()]  # 去除空白段落
    print(f"文章标题: {title}")
    print(f"共分割出 {len(paragraphs)} 个段落。")  # 打印段落数量以检查分割是否正确

    # 加载对应标题的图片文件夹
    image_folder = os.path.join(r"D:\move11\csdn\csdn\图片", title)
    if not os.path.exists(image_folder):
        print(f"警告: 找不到图片文件夹 '{image_folder}'")
        continue

    # 加载文件夹中的所有图片
    image_paths = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if
                          img.endswith(('.png', '.jpg', '.jpeg'))])

    # 使用列表存储预处理后的图像和有效路径
    images = []
    valid_image_paths = []  # 用于存储有效的图像路径
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            images.append(preprocess(img).unsqueeze(0).to(device))
            valid_image_paths.append(image_path)  # 只添加有效的路径
        except UnidentifiedImageError:
            print(f"警告: 无法处理图像文件 '{image_path}': 图片无法识别")
            continue  # 放弃当前图像，继续下一个
        except Exception as e:
            print(f"警告: 无法处理图像文件 '{image_path}': {e}")
            continue  # 放弃当前图像，继续下一个

    # 如果没有有效图片，跳过处理
    if not images:
        print(f"警告: 图片文件夹 '{image_folder}' 中没有找到有效图片")
        continue

    # 计算每张图片与所有段落的相似度
    text_tokens = clip.tokenize(paragraphs).to(device)

    with torch.no_grad():
        # 提取文本特征
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)  # 归一化

        # 使用 zip 同时迭代有效图像和路径
        for image, image_path in zip(images, valid_image_paths):
            image_feature = model.encode_image(image)
            image_feature /= image_feature.norm(dim=-1, keepdim=True)  # 归一化

            # 计算相似度
            similarities = torch.matmul(image_feature, text_features.T)
            probs = similarities.softmax(dim=-1).cpu().numpy()

            # 找到相似度最高的段落
            best_match_idx = probs.argmax()
            best_match_prob = probs[0, best_match_idx]

            # 输出匹配结果
            print(f"图片 '{image_path}' 与段落 {best_match_idx + 1} 的相似度概率: {best_match_prob:.4f}")

            # 创建目录以保存配对结果
            match_folder = os.path.join(output_folder, title)
            os.makedirs(match_folder, exist_ok=True)  # 确保创建对应的文件夹

            # 保存配对结果到指定文件夹
            output_image_path = os.path.join(match_folder,
                                             f"{title}_{valid_image_paths.index(image_path) + 1}.png")
            output_text_path = os.path.join(match_folder, f"{title}_{valid_image_paths.index(image_path) + 1}.txt")

            # 保存图片
            try:
                original_image = Image.open(image_path)  # 使用原始路径
                original_image.save(output_image_path)
            except Exception as e:
                print(f"保存图片时出错 '{image_path}' 到 '{output_image_path}': {e}")
                continue  # 放弃当前图片，继续下一个

            # 保存匹配的段落文本
            with open(output_text_path, "w", encoding="utf-8") as f:
                f.write(paragraphs[best_match_idx])

print("所有配对结果已保存。")