import time
import requests
from PIL import Image
from io import BytesIO
import ddddocr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os
import random
import math
import numpy as np
from captcha_recognizer.recognizer import Recognizer
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions

def url_to_image(url, savepath):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image.save(savepath)
    except Exception as e:
        print(e)

def gettrack(distance):
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 3 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current + 3 < distance:
            if current < mid:
                # 加速度为正6
                a = 6
            else:
                # 加速度为负9
                a = -9
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += round(move)
            # 加入轨迹
            track.append(round(move))
        sum = 0
        if distance > current:
            end = distance - current
            track.append(round(end))
        for i in range(0, len(track)):
            sum = sum + track[i]
        # print(track)
        # print(sum)
        return track

def distant_trans(target):
    return (10 * math.sqrt(14200 * target + 5929) - 770) / 71

def distantcon_v2(hkpath, qkpath):
    recognizer = Recognizer()
    box, confidence = recognizer.identify_gap(source=qkpath, verbose=False)
    target = 0
    try:
        target = box[0]
    except:
        print('没有找到目标')
        return
    print(f'Target position: {target}')
    rendersize = distant_trans(target)
    print(f'Render size: {rendersize}')
    return rendersize

hkpathroot = r'D:\2024年工作\知网数据库下载\\'
qkpathroot = r'D:\2024年工作\知网数据库下载\\'

def huakuaicon_v2(driver, pdfpath):
    try:
        blockeles = driver.find_elements(By.ID, 'aliyunCaptcha-sliding-slider')
        if len(blockeles) < 1:
            print("没有找到滑块")
            return False
    except Exception as e:
        print('没有找到滑块', e)
        return False

    hkimg = driver.find_element(By.ID, 'aliyunCaptcha-puzzle').get_attribute('src')
    qkimg = driver.find_element(By.ID, 'aliyunCaptcha-img').get_attribute('src')

    picpath = pdfpath + "\\图片"

    if not os.path.exists(picpath):
        os.makedirs(picpath)
    
    # 使用唯一标识符命名图片文件
    unique_id = str(int(time.time() * 1000)) + "_" + str(random.randint(1000, 9999))
    hkpath = picpath + f'\\滑块图片_{unique_id}.png'
    qkpath = picpath + f'\\缺口图片_{unique_id}.png'

    url_to_image(hkimg, hkpath)
    url_to_image(qkimg, qkpath)
    time.sleep(random.uniform(2, 3))
    distant = distantcon_v2(hkpath, qkpath)
    huakuai = driver.find_element(By.ID, "aliyunCaptcha-sliding-slider")
    action = ActionChains(driver)
    action.click_and_hold(huakuai).perform()
    time.sleep(random.uniform(0.8, 1.2))

    print('开始滑动...')
    track = gettrack(distant)
    for x in track:
        action.move_by_offset(xoffset=x, yoffset=0).perform()
        print(f'Moved by offset: {x}, Current X: {huakuai.location["x"]}')
    action.release().perform()
    time.sleep(random.uniform(2, 3))
    return True

# 设置 ChromeDriver 路径
# driver = webdriver.Chrome(service=Service(r"D:\多模态\chromedriver-win32\chromedriver-win32\chromedriver.exe"))
pdfpath = r'D:\2024年工作\知网数据库下载'
option=webdriver.ChromeOptions()
option.add_experimental_option("detach",True) #True让浏览器不会自动关闭
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=option,service=Service(r"D:\多模态\chromedriver-win32\chromedriver-win32\chromedriver.exe"))
# 打开目标网页
driver.get(r'https://bar.cnki.net/bar/verify/index.html?platform=nxgp&returnUrl=https%3A%2F%2Fbar.cnki.net%2Fbar%2Fdownload%2Forder%3Fid%3DPmp%252F5es3RB81cmauPwpbvsPMJcfwHgIZAnUyOJG6KdrCpOSDrTKNGQdBiFAHwa0KqMHwmhRM35krHRI2Tq6rMgqO7Dm3aTp1AQkJ96lSPV57b5mY%252FmsIpB5E%252FKF94iQVwddxEU3rL3oTHoiWc6PitFK57xT%252B8LhM%252BfEqYWvBGm0igmLMld3nSvbU4a5%252BOkNaUlSU0HSLnl9m7MwOtW%252FIk704DodxeHyMtmh5MVNvCsxlgv7q8C%252BP7FPVW3hwYPcq4VRMY0JBbjbLmfwjvao1dw%253D%253D%26source%3D%26isMobile%3Dfalse%26rb%3DEveryNTimes%26showpage%3D1&lang=zh-CN&ip=111.203.17.61&errorcode=3')  # 替换为目标网页 URL
# 解决验证码
# huakuaicon_v2(driver, pdfpath)
script = 'Object.defineProperty(navigator,"webdriver",{get:() => undefined,});'
#运行Javascript
driver.execute_script(script)

# 等待业务请求完成
time.sleep(999)



