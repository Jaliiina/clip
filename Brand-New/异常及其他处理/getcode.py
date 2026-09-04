import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_captcha_url(driver):
    try:
        hkimg = driver.find_element(By.ID, 'aliyunCaptcha-puzzle').get_attribute('src')
        qkimg = driver.find_element(By.ID, 'aliyunCaptcha-img').get_attribute('src')
        return hkimg, qkimg
    except Exception as e:
        print(f"Error getting captcha URL: {e}")
        return None

# 设置 ChromeDriver 路径
chrome_options = Options()
service = Service()  # 请替换为你的chromedriver路径
driver = webdriver.Chrome(service=service, options=chrome_options)

# 打开目标网页
url = r'https://bar.cnki.net/bar/verify/index.html?platform=nxgp&returnUrl=https%3A%2F%2Fbar.cnki.net%2Fbar%2Fdownload%2Forder%3Fid%3DPmp%252F5es3RB81cmauPwpbvsPMJcfwHgIZAnUyOJG6KdrCpOSDrTKNGQdBiFAHwa0KqMHwmhRM35krHRI2Tq6rMgqO7Dm3aTp1AQkJ96lSPV57b5mY%252FmsIpB5E%252FKF94iQVwddxEU3rL3oTHoiWc6PitFK57xT%252B8LhM%252BfEqYWvBGm0igmLMld3nSvbU4a5%252BOkNaUlSU0HSLnl9m7MwOtW%252FIk704DodxeHyMtmh5MVNvCsxlgv7q8C%252BP7FPVW3hwYPcq4VRMY0JBbjbLmfwjvao1dw%253D%253D%26source%3D%26isMobile%3Dfalse%26rb%3DEveryNTimes%26showpage%3D1&lang=zh-CN&ip=111.203.17.61&errorcode=3'
driver.get(url)
time.sleep(5)

# 创建或打开txt文件以保存验证码图片地址
output_dir = r'D:\2024年工作\知网数据库下载\url'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_counter = 5445

while True:
    hk_url, qk_url = get_captcha_url(driver)
    if hk_url and qk_url:
        file_counter += 1
        output_file_path = os.path.join(output_dir, f'captcha_urls_{file_counter}.txt')
        with open(output_file_path, 'w') as file:
            file.write(hk_url + '\n')
            file.write(qk_url + '\n')
            print(f"Captcha URLs saved to: {output_file_path}")

    # 刷新页面以获取新的验证码
    driver.refresh()
    time.sleep(random.uniform(3, 5))  # 等待页面加载新验证码



