'''
下载并解压 MinerU 解析结果的 ZIP 压缩包，仅下载解压。
'''
import os
import time
import zipfile
import requests
from urllib.parse import urlparse
from typing import Optional, Dict, Any


def download_and_extract_mineru_result(
    zip_url: str,
    data_id: Optional[str] = None,
    file_name: Optional[str] = None,
    download_dir: str = "./mineru_downloads",
    extract_dir: str = "./mineru_extracted",
    skip_if_exists: bool = True,
    timeout: int = 60,
    chunk_size: int = 8192
) -> Dict[str, Any]:
    """
    下载并解压 MinerU 解析结果的 ZIP 压缩包。

    Args:
        zip_url (str): MinerU 返回的 full_zip_url
        data_id (str, optional): 用于命名子目录的业务 ID（推荐提供）
        file_name (str, optional): 原始文件名（用于 fallback 命名）
        download_dir (str): ZIP 文件保存目录，默认 ./mineru_downloads
        extract_dir (str): 解压目标目录，默认 ./mineru_extracted
        skip_if_exists (bool): 若 ZIP 已存在是否跳过下载
        timeout (int): 请求超时时间（秒）
        chunk_size (int): 下载分块大小（字节）

    Returns:
        dict: 包含以下字段
            - zip_path: 本地 ZIP 路径
            - extract_path: 本地解压路径
            - success: 是否成功
            - error: 错误信息（如有）
    """
    # 确定子目录名称
    if data_id:
        subdir_name = data_id
    elif file_name:
        subdir_name = os.path.splitext(file_name)[0]
    else:
        # 从 URL 提取文件名作为 fallback
        parsed = urlparse(zip_url)
        basename = os.path.basename(parsed.path)
        subdir_name = basename.split('.')[0] or "unknown"

    # 构建路径
    safe_subdir = "".join(c if c.isalnum() or c in ('_', '-', '.') else '_' for c in subdir_name)
    zip_save_dir = os.path.join(download_dir, safe_subdir)
    extract_target_dir = os.path.join(extract_dir, safe_subdir)

    os.makedirs(zip_save_dir, exist_ok=True)
    os.makedirs(extract_target_dir, exist_ok=True)

    # ZIP 文件名
    zip_filename = os.path.basename(urlparse(zip_url).path) or f"{safe_subdir}.zip"
    zip_path = os.path.join(zip_save_dir, zip_filename)

    result = {
        "zip_path": zip_path,
        "extract_path": extract_target_dir,
        "success": False,
        "error": None
    }

    # 检查是否已存在
    if skip_if_exists and os.path.isfile(zip_path):
        if os.path.isdir(extract_target_dir) and os.listdir(extract_target_dir):
            result["success"] = True
            return result

    # 下载 ZIP
    try:
        resp = requests.get(zip_url, stream=True, timeout=timeout)
        resp.raise_for_status()

        with open(zip_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        err_msg = f"下载失败: {e}"
        result["error"] = err_msg
        return result

    # 解压 ZIP
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_target_dir)
        result["success"] = True
    except Exception as e:
        err_msg = f"解压失败: {e}"
        result["error"] = err_msg
        return result

    return result


# ======================
# 批量处理示例（配合上一个函数的结果）
# ======================
def batch_download_and_extract(results: list, **kwargs) -> list:
    """
    批量下载并解压多个 MinerU 解析结果。

    Args:
        results (list): 来自 batch_parse_local_files 的 results 列表
        **kwargs: 传递给 download_and_extract_mineru_result 的参数

    Returns:
        list: 每个文件的处理结果字典列表
    """
    outputs = []
    for res in results:
        if res["state"] != "done":
            outputs.append({
                "file_name": res.get("file_name"),
                "data_id": res.get("data_id"),
                "success": False,
                "error": f"任务未完成，状态: {res['state']}"
            })
            continue

        out = download_and_extract_mineru_result(
            zip_url=res["full_zip_url"],
            data_id=res.get("data_id"),
            file_name=res.get("file_name"),
            **kwargs
        )
        outputs.append(out)
    return outputs


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    # 示例：单个文件处理
    sample_url = "https://cdn-mineru.openxlab.org.cn/pdf/xxxxxx.zip"
    result = download_and_extract_mineru_result(
        zip_url=sample_url,
        data_id="report_2025",
        download_dir="./downloads",
        extract_dir="./output",
        skip_if_exists=True
    )

    if result["success"]:
        print(f"✅ 成功！解压路径: {result['extract_path']}")
    else:
        print(f"❌ 失败: {result['error']}")

    # 示例：批量处理（假设你已有解析结果列表）
    # fake_results = [
    #     {"state": "done", "full_zip_url": "...", "data_id": "doc1", "file_name": "a.pdf"},
    #     {"state": "failed", "err_msg": "格式不支持"}
    # ]
    # batch_out = batch_download_and_extract(fake_results, download_dir="./downloads")