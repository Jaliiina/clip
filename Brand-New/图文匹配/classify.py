import os
import json
import base64
from openai import OpenAI

# 初始化火山引擎客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=""  # 请填入你的 API Key
)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_max_json(text):
    stack = []
    start_index = -1
    max_json_str = ''
    for i, char in enumerate(text):
        if char == '[':
            if not stack:
                start_index = i
            stack.append(char)
        elif char == ']':
            if stack:
                stack.pop()
                if not stack and start_index != -1:
                    max_json_str = text[start_index:i + 1]
    return max_json_str

def llm_progressing(image_path):
    print("----- standard request -----")
    try:
        base64_image = encode_image(image_path)
        messages = [
            {
                "role": "system",
                "content": """
                            你的任务是对图片进行分类，图片为科技相关论文中所引用的图。对于图片分类，按照以下类型进行划分：

                            数据分析图
                            流程原理图
                            实物观测图
                            功能模块图
                            界面交互图
                            其他

                            对于每一张图片，以json格式返回图片类型（type）这一信息。

                            例如：
                            [
                            {"type":  "数据分析图"}
                            ]

                            请确保准确分类每一张图片，仅返回一条type信息，。
                            """
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请对图片进行分类。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        completion = client.chat.completions.create(
            model="ep-20250212160911-zsp7r",
            messages=messages
        )
        response = extract_max_json(completion.choices[0].message.content)
        print(response)
        return response
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def extract_and_save_image_info(input_folder):
    for root, _, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith('.jpg'):
                file_path = os.path.join(root, filename)
                structured_data_str = llm_progressing(file_path)
                if structured_data_str:
                    try:
                        structured_data = json.loads(structured_data_str)
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON from {filename}")
                        continue

                    output_file_path = os.path.join(root, f"{os.path.splitext(filename)[0]}.json")
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        json.dump(structured_data, output_file, ensure_ascii=False, indent=4)

# Example usage:
input_folder = r'D:\多模态\图文对\temp\temp'
extract_and_save_image_info(input_folder)




