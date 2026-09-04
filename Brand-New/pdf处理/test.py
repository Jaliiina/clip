'''
示例使用 MinerU API 批量解析本地文件（PDF/DOC/PPT/图片等）并下载解压 MinerU 解析结果的 ZIP 压缩包。
'''
import MinerU.mineru_api as mineru_api
import os
if __name__ == "__main__":
    # 单个文件处理示例
    mineru_api.run_batch_download_and_extract(
        files=['./test_files/基于自适应无迹卡尔曼的机器人室内定位算法_洪宇.pdf'], # 需要解析的文件列表，请根据实际情况修改
        model_version="vlm", # 模型版本，可选 "pipeline" 或 "vlm",前者速度更快但效果较差，后者效果更好但速度较慢
        download_dir='./test_output_vlm/mineru_zip', # ZIP 下载文件夹路径，请根据实际情况修改
        extract_dir='./test_output_vlm/mineru_unzip' # 解压输出文件夹路径，请根据实际情况修改
    )
    # # 批量文件夹处理示例(解析指定文件夹下的所有符合类型的文件)
    # mineru_api.running_folder(
    #     floder_path='./test_files', # 需要解析的文件夹路径，请根据实际情况修改
    #     file_type=('.pdf'), # 指定解析的文件类型
    #     model_version="vlm", # 模型版本，可选 "pipeline" 或 "vlm",前者速度更快但效果较差，后者效果更好但速度较慢
    #     output_dir='./test_output_vlm') # 输出文件夹路径，请根据实际情况修改
    print("All tests passed.")