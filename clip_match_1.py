import torch
import cn_clip.clip as clip
from PIL import Image, UnidentifiedImageError
from cn_clip.clip import load_from_name
import os
import re
import shutil

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"

# 加载模型
model, preprocess = load_from_name("ViT-B-16", device=device, download_root='./')
model.eval()

# 设置文件路径
root_folder = r"D:\move11\result"  # 顶层 result 文件夹路径
output_folder = r"D:\move11\配对结果"  # 保存配对结果的文件夹
os.makedirs(output_folder, exist_ok=True)

# 迭代每个文章文件夹
for article_folder in os.listdir(root_folder):
    article_path = os.path.join(root_folder, article_folder)
    if not os.path.isdir(article_path):
        continue  # 如果不是文件夹，跳过

    # 读取文章内容
    txt_file = os.path.join(article_path, f"{article_folder}.txt")
    if not os.path.exists(txt_file):
        print(f"警告: 找不到文章内容文件 '{txt_file}'")
        continue

    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 使用双换行 '\n\n' 进行初步分割
    paragraphs = re.split(r'\n\s*\n', content)

    paragraphs = [para.strip() for para in paragraphs if para.strip()]  # 去除空白段落

    print(f"文章 '{article_folder}' 共分割出 {len(paragraphs)} 个段落。")

    # 加载对应图片文件夹
    image_folder = os.path.join(article_path, "图片")
    if not os.path.exists(image_folder):
        print(f"警告: 找不到图片文件夹 '{image_folder}'")
        continue

    # 加载文件夹中的所有图片
    image_paths = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if
                          img.endswith(('.png', '.jpg', '.jpeg'))])

    # 使用列表存储预处理后的图像和有效路径
    images = []
    valid_image_paths = []
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            images.append(preprocess(img).unsqueeze(0).to(device))
            valid_image_paths.append(image_path)  # 只添加有效的路径
        except UnidentifiedImageError:
            print(f"警告: 无法处理图像文件 '{image_path}': 图片无法识别")
            continue
        except Exception as e:
            print(f"警告: 无法处理图像文件 '{image_path}': {e}")
            continue

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
            match_folder = os.path.join(output_folder, article_folder)
            os.makedirs(match_folder, exist_ok=True)

            # 保存配对结果到指定文件夹
            output_image_path = os.path.join(match_folder,
                                             f"{article_folder}_{valid_image_paths.index(image_path) + 1}.png")
            output_text_path = os.path.join(match_folder,
                                            f"{article_folder}_{valid_image_paths.index(image_path) + 1}.txt")

            # 保存图片
            try:
                original_image = Image.open(image_path)  # 使用原始路径
                original_image.save(output_image_path)
            except Exception as e:
                print(f"保存图片时出错 '{image_path}' 到 '{output_image_path}': {e}")
                continue

            # 保存匹配的段落文本
            with open(output_text_path, "w", encoding="utf-8") as f:
                f.write(paragraphs[best_match_idx])

    # 删除已经处理过的文章文件夹
    try:
        shutil.rmtree(article_path)  # 删除整个文件夹及其内容
        print(f"已删除文件夹 '{article_path}'")
    except Exception as e:
        print(f"删除文件夹 '{article_path}' 时出错: {e}")
