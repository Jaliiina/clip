'''
批量解析本地文件（PDF/DOC/PPT/图片等）并下载解压 MinerU 解析结果的 ZIP 压缩包,整合请求及下载解压。
'''
import MinerU.mineru as mineru
import MinerU.download as download
import os
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())

def run_batch_parse_local_files(files=None, model_version="pipeline"):
    TOKEN = os.getenv("MINERU_API_TOKEN")
    if not TOKEN:
        raise ValueError("请设置环境变量 MINERU_API_TOKEN")
    files = files
    output = mineru.batch_parse_local_files(
        file_paths=files,
        model_version=model_version,
        token=TOKEN,
        poll_interval=5,
        max_wait_time=300,
        use_ocr=True,
    )
    return output
def run_batch_download_and_extract(files=None, model_version="pipeline", download_dir='mineru_zip', extract_dir='mineru_unzip'):
    results = run_batch_parse_local_files(files=files, model_version=model_version)["results"]
    outputs = download.batch_download_and_extract(
        results=results,
        download_dir=download_dir,
        extract_dir=extract_dir,
        skip_if_exists=True
    )
    for out in outputs:
        if out["success"]:
            print(f"✅ 成功！文件: {out['zip_path']} 解压路径: {out['extract_path']}")
        else:
            print(f"❌ 失败！文件: {out['zip_path']} 错误: {out['error']}")
    return outputs
def running_folder(floder_path, file_type=('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png'), model_version="pipeline", output_dir='./mineru_output'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    files = [os.path.join(floder_path, f) for f in os.listdir(floder_path) if f.endswith((file_type))]
    run_batch_download_and_extract(files=files, model_version=model_version, download_dir=output_dir + "./mineru_zip", extract_dir=output_dir + "./mineru_unzip")
if __name__ == "__main__":
    running_folder(floder_path='./test_files')
    