'''
批量解析本地文件（PDF/DOC/PPT/图片等）使用 MinerU API，仅请求解析。
'''
import os
import time
import requests
from typing import List, Dict, Optional, Any
from tqdm import tqdm


def batch_parse_local_files(
    file_paths: List[str],
    token: str,
    model_version: str = "pipeline",
    options: Optional[Dict[str, Any]] = None,
    callback: Optional[str] = None,
    seed: Optional[str] = None,
    extra_formats: Optional[List[str]] = None,
    poll_interval: int = 5,
    max_wait_time: int = 3600,  # 最多等待1小时
    upload_retries: int = 3,
    verbose: bool = True,
    use_ocr: bool = True
) -> Dict[str, Any]:
    """
    批量解析本地文件（PDF/DOC/PPT/图片等）使用 MinerU API。

    Args:
        file_paths (List[str]): 本地文件路径列表（最多200个）
        token (str): MinerU API Token
        model_version (str): 模型版本，"pipeline" 或 "vlm"，默认 "pipeline"
        options (dict, optional): 全局解析选项，如 {"enable_table": True, "language": "fr"}
        callback (str, optional): 回调 URL
        seed (str, optional): 回调签名用的随机字符串（若使用 callback 必须提供）
        extra_formats (List[str], optional): 额外导出格式，如 ["docx", "html"]
        poll_interval (int): 轮询间隔（秒）
        max_wait_time (int): 最大等待时间（秒）
        upload_retries (int): 文件上传失败重试次数
        verbose (bool): 是否打印进度信息

    Returns:
        dict: 包含 batch_id 和每个文件最终状态的字典
    """
    if not file_paths:
        raise ValueError("file_paths 不能为空")
    if len(file_paths) > 200:
        raise ValueError("单次最多支持 200 个文件")

    # 构造 files 列表
    files_meta = []
    for fp in file_paths:
        if not os.path.isfile(fp):
            raise FileNotFoundError(f"文件不存在: {fp}")
        name = os.path.basename(fp)
        data_id = os.path.splitext(name)[0]  # 默认用文件名（不含后缀）作为 data_id
        files_meta.append({"name": name, "data_id": data_id, "is_ocr": use_ocr})

    # 构建请求体
    payload = {
        "files": files_meta,
        "model_version": model_version
    }

    if options:
        payload.update({k: v for k, v in options.items() if k not in ["files", "model_version"]})

    if callback:
        if not seed:
            raise ValueError("使用 callback 时必须提供 seed")
        payload["callback"] = callback
        payload["seed"] = seed

    if extra_formats:
        payload["extra_formats"] = extra_formats

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 1: 申请上传链接
    apply_url = "https://mineru.net/api/v4/file-urls/batch"
    try:
        resp = requests.post(apply_url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") != 0:
            raise RuntimeError(f"申请上传链接失败: {result.get('msg')}")
    except Exception as e:
        raise RuntimeError(f"申请上传链接异常: {e}")

    batch_id = result["data"]["batch_id"]
    file_urls = result["data"]["file_urls"]

    if verbose:
        print(f"✅ 成功申请 batch_id: {batch_id}，共 {len(file_urls)} 个文件")

    # Step 2: 上传文件
    for i, (fp, upload_url) in enumerate(zip(file_paths, file_urls)):
        for attempt in range(upload_retries + 1):
            try:
                with open(fp, 'rb') as f:
                    # 注意：不要设置 Content-Type！
                    upload_resp = requests.put(upload_url, data=f, timeout=300)
                if upload_resp.status_code == 200:
                    if verbose:
                        print(f"📤 [{i+1}/{len(file_paths)}] {os.path.basename(fp)} 上传成功")
                    break
                else:
                    raise Exception(f"HTTP {upload_resp.status_code}")
            except Exception as e:
                if attempt < upload_retries:
                    if verbose:
                        print(f"⚠️ 上传失败（尝试 {attempt+1}/{upload_retries+1}），重试中...: {e}")
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise RuntimeError(f"❌ 文件 {fp} 上传失败，已达最大重试次数: {e}")

    # Step 3: 轮询任务状态直到完成或超时
    status_url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
    start_time = time.time()

    if verbose:
        print("⏳ 开始轮询解析状态...")

    while True:
        try:
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            status_resp.raise_for_status()
            status_data = status_resp.json()

            if status_data.get("code") != 0:
                raise RuntimeError(f"查询状态失败: {status_data.get('msg')}")

            results = status_data["data"]["extract_result"]
            all_done = True
            pending_count = 0
            for r in results:
                state = r["state"]
                if state in ("failed", "done"):
                    continue
                else:
                    all_done = False
                    if state in ("pending", "running", "waiting-file", "converting"):
                        pending_count += 1

            if all_done:
                if verbose:
                    print("✅ 所有文件解析完成！")
                return {
                    "batch_id": batch_id,
                    "results": results
                }

            if time.time() - start_time > max_wait_time:
                raise TimeoutError(f"解析超时（>{max_wait_time}秒），当前状态: {[r['state'] for r in results]}")

            if verbose:
                done = sum(1 for r in results if r["state"] == "done")
                failed = sum(1 for r in results if r["state"] == "failed")
                print(f"📊 进度: {done} 完成, {failed} 失败, {pending_count} 处理中...")

            time.sleep(poll_interval)

        except Exception as e:
            if verbose:
                print(f"⚠️ 轮询异常: {e}，继续重试...")
            time.sleep(poll_interval)


# ======================
# 示例用法
# ======================
if __name__ == "__main__":
    import os
    from dotenv import find_dotenv, load_dotenv

    _ = load_dotenv(find_dotenv())
    TOKEN = os.getenv("MINERU_API_TOKEN")  # 建议从环境变量读取
    if not TOKEN:
        raise ValueError("请设置环境变量 MINERU_API_TOKEN")
    print("使用的 Token:", TOKEN)
    files = ["./sample.pdf"]  # 替换为你的文件路径

    try:
        output = batch_parse_local_files(
            file_paths=files,
            token=TOKEN,
            model_version="pipeline",
            options={
                "language": "ch",
                "enable_table": True,
                "enable_formula": True
            },
            poll_interval=10,
            max_wait_time=1800,  # 最多等30分钟
            verbose=True
        )

        # 打印结果
        for res in output["results"]:
            if res["state"] == "done":
                print(f"📄 {res['file_name']} → 下载: {res['full_zip_url']}")
            else:
                print(f"❌ {res['file_name']} 失败: {res.get('err_msg', '未知错误')}")

    except Exception as e:
        print("💥 批量解析失败:", e)