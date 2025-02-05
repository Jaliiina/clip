import os
import torch
import cn_clip.clip as clip
from PIL import Image, UnidentifiedImageError
from cn_clip.clip import load_from_name
import shutil

# 设置设备
device = "cuda" if torch.cuda.is_available() else "cpu"

# 加载模型
model, preprocess = load_from_name("ViT-B-16", device=device, download_root='./')
model.eval()

# 定义类别名称
categories =["数据统计图","流程路线图","实物示例图"]

# 将类别名称转换为 CLIP 文本特征
category_tokens = clip.tokenize(categories).to(device)
with torch.no_grad():
    category_features = model.encode_text(category_tokens)
    category_features /= category_features.norm(dim=-1, keepdim=True)  # 归一化

input_folder = r"D:\move11\分类前"
output_folder = r"D:\move11\分类图片"
os.makedirs(output_folder, exist_ok=True)

# 设置相似度阈值
similarity_threshold = 0.3

# 遍历文件夹中的所有图片文件
for img_name in os.listdir(input_folder):
    img_path = os.path.join(input_folder, img_name)

    # 检查文件是否为有效图片
    try:
        img = Image.open(img_path)
        image_input = preprocess(img).unsqueeze(0).to(device)
    except UnidentifiedImageError:
        print(f"警告: 无法处理图像文件 '{img_path}': 图片无法识别")
        continue  # 跳过无法处理的文件
    except Exception as e:
        print(f"警告: 无法处理图像文件 '{img_path}': {e}")
        continue  # 跳过其他异常文件

    # 计算图像特征
    with torch.no_grad():
        image_feature = model.encode_image(image_input)
        image_feature /= image_feature.norm(dim=-1, keepdim=True)  # 归一化

        # 计算图像与类别的相似度
        similarities = torch.matmul(image_feature, category_features.T)
        probs = similarities.softmax(dim=-1).cpu().numpy()

    # 找到相似度最高的类别
    best_match_idx = probs.argmax()
    best_category = categories[best_match_idx]
    best_similarity = probs[0][best_match_idx]  # 最高相似度

    # 如果相似度超过阈值，则保存图片
    if best_similarity > similarity_threshold:
        # 构建新的文件名
        new_img_name = f"{os.path.splitext(img_name)[0]}_{best_category}{os.path.splitext(img_name)[1]}"
        new_img_path = os.path.join(output_folder, new_img_name)

        # 复制图片并重命名到新的文件夹
        shutil.copy(img_path, new_img_path)
        print(f"图片 '{img_name}' 分类为 '{best_category}'（相似度: {best_similarity*100:.2f}%)，已保存为 '{new_img_name}'")
    else:
        print(f"图片 '{img_name}' 相似度低于阈值（{best_similarity*100:.2f}%)，未保存")

print("所有图片处理完成。")
