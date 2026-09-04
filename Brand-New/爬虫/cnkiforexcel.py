'''
CNKI论文题录下载

基本设置与cnki.py相同。基本上不需要验证码，所以直接删除，如需要验证码，请参考cnki.py的验证码部分。
'''
from selenium import webdriver
import re
import time
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

global initdata
bgdate = '2023-01-01'
initdate = '2026-06-30'

def downloadexcel(driver):
    # 开始导出文献
    li_uploadlist = driver.find_element(By.CLASS_NAME, 'secondUl').find_elements(By.CSS_SELECTOR, 'li')
    selfdef = li_uploadlist[-1].find_element(By.CSS_SELECTOR, 'a')
    print("自定义下载")
    # selfdef.click()
    driver.execute_script("arguments[0].click();", selfdef)
    windows = driver.window_handles
    print("当前窗口个数：", len(windows))
    if len(windows) > 1:  # check if there is more than one window  
        driver.switch_to.window(windows[1])  
    else:  
        print("No second window available.")  

    print(driver.current_url)
    time.sleep(3)
    WebDriverWait(driver, 20, 0.5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'row-btns')))
    # 全选
    cur_selall = driver.find_element(By.CLASS_NAME, 'row-btns').find_elements(By.CSS_SELECTOR, 'a')[0]
    # cur_selall.click()
    driver.execute_script("arguments[0].click();", cur_selall)
    download_excel = driver.find_element(By.ID, 'litoexcel').find_element(By.CSS_SELECTOR, 'a')
    # download_excel.click()
    driver.execute_script("arguments[0].click();", download_excel)
    time.sleep(5)
    #aaa
    driver.close()

global next_flag
next_flag=False

def cnkipaperfordata(keywords, keywords2):
    global initdate
    global next_flag
    download_dir = r'D:\2024年工作\知网数据库下载'  # 路径一定是斜杠，不能是反斜杠
    chrome_options = Options()

    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': download_dir,
             "directory_upgrade": True}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=chrome_options)

    #driver = webdriver.Chrome('F:\ChromDriver\chromedriver_win32\chromedriver.exe')
    #driver.get('https://kns.cnki.net/KNS8/AdvSearch?dbcode=SCOD&searchType=majorSearch')
    driver.get('https://kns.cnki.net/kns8/AdvSearch?dbprefix=SCDB&&crossDbcodes=CJFQ%2CCDMD%2CCIPD%2CCCND%2CCISD%2CSNAD%2CBDZK%2CCCJD%2CCCVD%2CCJFN%2CCCJD')
    driver.maximize_window()  # 最大化窗口
    time.sleep(3)
    select_eleddlist=driver.find_element(By.ID, 'gradetxt').find_elements(By.CSS_SELECTOR, 'dd')
    # 获取第一个选择项（保持不变）
    sel_dd_1 = select_eleddlist[0]
    dd_cli_1 = sel_dd_1.find_element(By.CLASS_NAME, 'sort.reopt')
    dd_cli_1.click()
    time.sleep(random.randint(2, 4))

    # 选择第一个下拉选项: 主题（保持不变）
    sel_li_1 = dd_cli_1.find_element(By.CSS_SELECTOR, '.sort-list li[data-val="SU"]')
    print(sel_li_1.get_attribute('outerHTML'))
    try:
        sel_li_1.click()
    except:
        print('没有找到元素')
    time.sleep(random.randint(2, 4))

    # 输入关键词到第一个文本框（保持不变）
    text_element_1 = sel_dd_1.find_element(By.CSS_SELECTOR, 'input[type="text"]')
    print('text_element_1:', text_element_1.get_attribute('outerHTML'))
    time.sleep(random.randint(2, 4))
    text_element_1.send_keys(keywords)
    time.sleep(random.randint(2, 4))

    # 修改逻辑操作为 NOT
    logical_sort = driver.find_element(By.CSS_SELECTOR, '.gradeSearch .sort.logical')
    logical_sort_default = logical_sort.find_element(By.CLASS_NAME, 'sort-default')
    logical_sort_default.click()
    time.sleep(random.randint(2, 4))

    not_option = logical_sort.find_element(By.CSS_SELECTOR, '.sort-list li:last-child a')
    print(not_option.get_attribute('outerHTML'))
    try:
        not_option.click()
    except:
        print('没有找到元素')
    time.sleep(random.randint(2, 4))

    # 获取第二个选择项
    sel_dd_2 = select_eleddlist[1]
    dd_cli_2 = sel_dd_2.find_element(By.CLASS_NAME, 'sort.reopt')
    dd_cli_2.click()
    time.sleep(random.randint(2, 4))

    # 选择第二个下拉选项: 关键词
    sel_li_2 = dd_cli_2.find_element(By.CSS_SELECTOR, '.sort-list li[data-val="SU"]')
    print(sel_li_2.get_attribute('outerHTML'))
    try:
        sel_li_2.click()
    except:
        print('没有找到元素')
    time.sleep(random.randint(2, 4))

    # 输入关键词到第二个文本框
    text_element_2 = sel_dd_2.find_element(By.CSS_SELECTOR, 'input[type="text"]')
    print('text_element_2:', text_element_2.get_attribute('outerHTML'))
    time.sleep(random.randint(2, 4))
    text_element_2.send_keys(keywords2)
    time.sleep(random.randint(2, 4))

    #去掉英文文献
    input=driver.find_element(By.CSS_SELECTOR, 'input[data-id="EN"]')
    try:
        input.click()
    except Exception as e:
        print(e)
    # input.click()
    time.sleep(3)
    #填写开始时间
    times=driver.find_element(By.CLASS_NAME, 'tit-date-box').find_elements(By.CSS_SELECTOR, 'input')
    #start_time=times[0]#.send_keys('2011-01-01')
    #start_time.send_keys('2011-01-01')
    date_txt_bg = driver.find_element(By.ID, 'datebox0')
    driver.execute_script("arguments[0].removeAttribute('readonly');", date_txt_bg)
    date_txt_bg.clear()  # 先清除原来的日期值
    date_txt_bg.send_keys(bgdate)
    #date_txt_bg.send_keys(initdate)
    #print('更新开始论文时间：',initdate)

    date_txt_end = driver.find_element(By.ID, 'datebox1')
    driver.execute_script("arguments[0].removeAttribute('readonly');", date_txt_end)
    date_txt_end.clear()  # 先清除原来的日期值
    # date_txt.send_keys('2010-01-01')
    date_txt_end.send_keys(initdate)
    print('更新结束论文时间：', initdate)

    print(times[0].get_attribute('outerHTML'))
    time.sleep(5)
    #start_time = time[0].send_keys('2011-01-01')
    searchbtn = driver.find_element(By.CLASS_NAME, 'btn-search')
    #searchbtn.click()
    driver.execute_script("arguments[0].click();", searchbtn)
    time.sleep(5)
    now_url = driver.current_url #当前页面
    print('主页:',now_url)

    # 只采集学术期刊
    print('只选择学术期刊')
    journal = driver.find_element(By.CSS_SELECTOR, 'a[resource="JOURNAL"]')
    journal.click()
    time.sleep(3)

    main_handle = driver.current_window_handle
    nextbutton=True
    count=1
    page_count=0
    while nextbutton == True:
        nextbutton = False
        print("第%s页" % count)
        if count>=page_count:
            #1、需要输入验证码
            vericodeele = driver.find_elements(By.CLASS_NAME, 'verifycode')
            if len(vericodeele) > 0:
                print('需要验证码')
                nextbutton = True
                continue
            time.sleep(3)
            # 2重新加载、
            reloadele=driver.find_elements(By.ID, 'reload-button')
            if len(reloadele) > 0:
                print('需要重新加载')
                reloadbtn=reloadele[0]
                reloadbtn.click()
                time.sleep(3)
                nextbutton = True
                continue


        try:
            #1、题录全选
            WebDriverWait(driver, 20, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'checkAll')))

            #倒叙排列，点击排序按钮

            #selallclick.click()
            # 开始点击全选
            selallclick = driver.find_element(By.CLASS_NAME, 'checkAll').find_element(By.CSS_SELECTOR, 'input')
            driver.execute_script("arguments[0].click();", selallclick)
            datelist=driver.find_element(By.CLASS_NAME, 'result-table-list').find_elements(By.CLASS_NAME, 'date')
            if (len(datelist)>0) and  count%10==1:
                initdates=datelist[0].get_attribute('innerHTML')
                #print(initdates)
                #initdate=initdates.split(' ')[1]
                initdate = re.findall('\d{4}-\d{2}-\d{2}', initdates)[0]
                print('更新initdate:', initdate)
        except Exception as e:
            driver.quit()
            print('提取题录失败，关闭网页:',e)
            nextbutton = False
            break

        time.sleep(2)

        if ((count%10)==0 and count>page_count):#500下载excel
            print('第%s个表格开始下载'%(count/10))
            downloadexcel(driver)
            windows = driver.window_handles
            print("当前有%s个窗口"%len(windows))
            driver.switch_to.window(main_handle)
            seldeleteall = driver.find_element(By.CLASS_NAME, 'checkcount').find_element(By.CSS_SELECTOR, 'a')
            seldeleteall.click()
            print('下载完成一次===========================\n')
        #2、翻页
        try:
            next_ele=driver.find_element(By.ID, 'Page_next_top')
            #next_ele.click()
            driver.execute_script("arguments[0].click();", next_ele)
            nextbutton = True
            time.sleep(3)
        except Exception as e:
            print("翻页失败",e)
            next_flag=True
            nextbutton = False
            if (count%25)!=0:
               downloadexcel(driver)
        count = count + 1

    driver.quit()

def spiderfordate(text):#增加日期
        global next_flag
        global initdate
        while ('2010-06-' in initdate)==False and next_flag==False:
            print("开始：initdate", initdate)
            try:
              cnkipaperfordata(text)
            except Exception as e:
                print(e)


from datetime import datetime
def rename_folder(old_path, new_name):
    # 构造新的文件夹路径
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    if  os.path.exists(new_path):
        #c# 获取当前时间，精确到秒
        now = datetime.now().replace(microsecond=0)
        print(now)
        formatted_time = now.strftime('%Y-%m-%d %H-%M-%S')
        os.rename(new_path, new_path+str(formatted_time))
    os.rename(old_path, new_path)
#新增：将页面处理函数全都放到以下函数
def setexcelcon(driver,pdfpath, subject):
    main_handle = driver.current_window_handle
    nextbutton = True
    count = 1
    page_count = 0
    #翻页采集
    while nextbutton == True:
        nextbutton = False
        print("第%s页" % count)
        if count >= page_count:
            # 1、需要输入验证码
            vericodeele = driver.find_elements(By.CLASS_NAME, 'verifycode')
            if len(vericodeele) > 0:
                print('需要验证码')
                nextbutton = True
                continue
            time.sleep(3)
            # 2重新加载、
            reloadele = driver.find_elements(By.ID, 'reload-button')
            if len(reloadele) > 0:
                print('需要重新加载')
                reloadbtn = reloadele[0]
                reloadbtn.click()
                time.sleep(3)
                nextbutton = True
                continue

        try:
            # 1、题录全选
            WebDriverWait(driver, 20, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'checkAll')))

            # 倒叙排列，点击排序按钮

            # selallclick.click()
            # 开始点击全选
            selallclick = driver.find_element(By.CLASS_NAME, 'checkAll').find_element(By.CSS_SELECTOR, 'input')
            driver.execute_script("arguments[0].click();", selallclick)
            datelist = driver.find_element(By.CLASS_NAME, 'result-table-list').find_elements(By.CLASS_NAME, 'date')
            if (len(datelist) > 0) and count % 10 == 1:
                initdates = datelist[0].get_attribute('innerHTML')
                # print(initdates)
                # initdate=initdates.split(' ')[1]
                initdate = re.findall('\d{4}-\d{2}-\d{2}', initdates)[0]
                print('更新initdate:', initdate)
        except Exception as e:
            driver.quit()
            print('提取题录失败，关闭网页:', e)
            nextbutton = False
            break

        time.sleep(2)

        if ((count % 10) == 0 and count > page_count):  # 500下载excel
            print('第%s个表格开始下载' % (count / 10))
            downloadexcel(driver)
            windows = driver.window_handles
            print("当前有%s个窗口" % len(windows))
            driver.switch_to.window(main_handle)
            seldeleteall = driver.find_element(By.CLASS_NAME, 'checkcount').find_element(By.CSS_SELECTOR, 'a')
            seldeleteall.click()
            print('下载完成一次===========================\n')
        # 2、翻页
        try:
            next_ele = driver.find_element(By.ID, 'Page_next_top')
            # next_ele.click()
            driver.execute_script("arguments[0].click();", next_ele)
            nextbutton = True
            time.sleep(3)
        except Exception as e:
            print("翻页失败", e)
            next_flag = True
            nextbutton = False
            if (count % 10) != 0:
                downloadexcel(driver)
                windows = driver.window_handles
                print("当前有%s个窗口" % len(windows))
                driver.switch_to.window(main_handle)
                seldeleteall = driver.find_element(By.CLASS_NAME, 'checkcount').find_element(By.CSS_SELECTOR, 'a')
                seldeleteall.click()
                print('该学科下载完成===========================\n')
        count = count + 1

    #进行修改名称，然后再重建一个文件夹
    rename_folder(pdfpath, subject)
    if not os.path.exists(pdfpath):
        # 如果文件夹不存在，则创建文件夹
        os.makedirs(pdfpath)


import os
#新增接口，增加学术期刊，
def cnkipaperfordatav2(text):
    global initdate
    global next_flag
    download_dir = r'D:\2024年工作\知网数据库下载'+"\\"+text+'\excel下载'  #路径一定是斜杠，不能是反斜杠，不能是双斜杠
    chrome_options = Options()
    print(download_dir)
    if not os.path.exists(download_dir):
        # 如果文件夹不存在，则创建文件夹
        os.makedirs(download_dir)

    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': download_dir,
             "directory_upgrade": True}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=chrome_options)

    #driver = webdriver.Chrome('F:\ChromDriver\chromedriver_win32\chromedriver.exe')
    #driver.get('https://kns.cnki.net/KNS8/AdvSearch?dbcode=SCOD&searchType=majorSearch')
    driver.get('https://kns.cnki.net/kns8/AdvSearch?dbprefix=SCDB&&crossDbcodes=CJFQ%2CCDMD%2CCIPD%2CCCND%2CCISD%2CSNAD%2CBDZK%2CCCJD%2CCCVD%2CCJFN%2CCCJD')
    driver.maximize_window()  # 最大化窗口
    time.sleep(3)
    select_eleddlist=driver.find_element(By.ID, 'gradetxt').find_elements(By.CSS_SELECTOR, 'dd')
    #获取第一个选择项
    sel_dd=select_eleddlist[0]
    dd_cli=sel_dd.find_element(By.CLASS_NAME, 'sort.reopt')
    dd_cli.click()
    time.sleep(3)
    #获取下拉选项:文献来源
    #sel_li=dd_cli.find_element(By.CLASS_NAME, 'sort-list').find_element(By.CSS_SELECTOR, 'li[data-val="LY"]')
    sel_li=dd_cli.find_element(By.CLASS_NAME, 'sort-list').find_element(By.CSS_SELECTOR, 'li[data-val="SU"]')
    print(sel_li.get_attribute('outerHTML'))
    sel_li.click()
    time.sleep(3)
    text_element = sel_dd.find_element(By.CSS_SELECTOR, 'input[type="text"]')
    print('text_element:',text_element.get_attribute('outerHTML'))
    time.sleep(3)
    text_element.send_keys(text)
    time.sleep(3)

    #去掉英文文献
    input=driver.find_element(By.CSS_SELECTOR, 'input[data-id="EN"]')
    input.click()
    time.sleep(3)
    #填写开始时间
    times=driver.find_element(By.CLASS_NAME, 'tit-date-box').find_elements(By.CSS_SELECTOR, 'input')
    #start_time=times[0]#.send_keys('2011-01-01')
    #start_time.send_keys('2011-01-01')
    date_txt_bg = driver.find_element(By.ID, 'datebox0')
    driver.execute_script("arguments[0].removeAttribute('readonly');", date_txt_bg)
    date_txt_bg.clear()  # 先清除原来的日期值
    date_txt_bg.send_keys('2010-08-24')
    #date_txt_bg.send_keys(initdate)
    #print('更新开始论文时间：',initdate)

    date_txt_end = driver.find_element(By.ID, 'datebox1')
    driver.execute_script("arguments[0].removeAttribute('readonly');", date_txt_end)
    date_txt_end.clear()  # 先清除原来的日期值
    # date_txt.send_keys('2010-01-01')
    date_txt_end.send_keys(initdate)
    print('更新结束论文时间：', initdate)

    print(times[0].get_attribute('outerHTML'))
    time.sleep(5)
    #start_time = time[0].send_keys('2011-01-01')
    searchbtn = driver.find_element(By.CLASS_NAME, 'btn-search')
    #searchbtn.click()
    driver.execute_script("arguments[0].click();", searchbtn)
    time.sleep(5)
    now_url = driver.current_url #当前页面
    print('主页:',now_url)

    # 只采集学术期刊
    print('只选择学术期刊')
    journal = driver.find_element(By.CSS_SELECTOR, 'a[resource="JOURNAL"]')
    journal.click()
    time.sleep(3)

    # 只选择核心期刊
    print('只选择北大核心期刊')
    LYBSMele = driver.find_element(By.CSS_SELECTOR, 'dl[groupid="LYBSM"]')
    driver.execute_script("arguments[0].class= '  ';", LYBSMele)
    LYBSMele.click()
    time.sleep(3)
    # print(LYBSMele.get_attribute('outerHTML'))
    # print(LYBSMele.get_attribute('innerHTML'))
    central = LYBSMele.find_element(By.CSS_SELECTOR, 'input[text="北大核心"]')
    central.click()
    time.sleep(3)

    # 分学科进行采集
    print('每个选项选择学科属性')
    cclele = driver.find_element(By.CSS_SELECTOR, 'dl[groupid="CCL"]')
    driver.execute_script("arguments[0].class= '  ';", cclele)
    cclele.click()
    time.sleep(3)
    # cclele = driver.find_element(By.CSS_SELECTOR, 'dd[field="CCL"]')
    ccllist = cclele.find_elements(By.CSS_SELECTOR, 'li')
    print(len(ccllist))
    j = 0
    while j < len(ccllist):
        if j > 9:
            driver.execute_script("arguments[0].style.display = 'list-item';", ccllist[j])
        # print(ccllist[j].get_attribute('outerHTML'))
        checkbox = ccllist[j].find_element(By.CSS_SELECTOR, 'input')
        print("\n===========选择学科%s,名称：%s" % (j, checkbox.get_attribute('title')))
        subject = checkbox.get_attribute('title')  # 获取学科类别
        # print(checkbox.get_attribute('outerHTML'))
        checkbox.click()  # 点击选中
        time.sleep(3)

        # 下载pdf文件
        setexcelcon(driver, download_dir, subject)

        windows = driver.window_handles
        print("当前有%s个窗口" % len(windows))
        # 下载完成之后需要再取消一下,需要重新获取一下当前的节点
        cclelev2 = driver.find_element(By.CSS_SELECTOR, 'dd[field="CCL"]')
        ccllistv2 = cclelev2.find_elements(By.CSS_SELECTOR, 'input[checked="checked"]')
        # checkbox = ccllistv2[0].find_element(By.CSS_SELECTOR, 'input')
        ccllistv2[0].click()
        time.sleep(2)

        # 重新获取一下自选框,取消完之后重新获取
        cclele = driver.find_element(By.CSS_SELECTOR, 'dd[field="CCL"]')
        ccllist = cclele.find_elements(By.CSS_SELECTOR, 'li')
        j = j + 1
    driver.quit()

def cnkipaperfordatav3(keywords):
    global initdate
    global next_flag
    download_dir = r'D:\2024年工作\知网数据库下载'  # 路径一定是斜杠，不能是反斜杠
    chrome_options = Options()

    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': download_dir,
             "directory_upgrade": True}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=chrome_options)

    #driver = webdriver.Chrome('F:\ChromDriver\chromedriver_win32\chromedriver.exe')
    #driver.get('https://kns.cnki.net/KNS8/AdvSearch?dbcode=SCOD&searchType=majorSearch')
    driver.get('https://kns.cnki.net/kns8/AdvSearch?dbprefix=SCDB&&crossDbcodes=CJFQ%2CCDMD%2CCIPD%2CCCND%2CCISD%2CSNAD%2CBDZK%2CCCJD%2CCCVD%2CCJFN%2CCCJD')
    driver.maximize_window()  # 最大化窗口
    
    # 等待手动输入检索条件
    search_condition = input("请输入检索条件后按回车继续: ")

    #去掉英文文献
    input_en = driver.find_element(By.CSS_SELECTOR, 'input[data-id="EN"]')
    try:
        input_en.click()
    except Exception as e:
        print(e)
    # input.click()
    time.sleep(3)
    #填写开始时间
    times=driver.find_element(By.CLASS_NAME, 'tit-date-box').find_elements(By.CSS_SELECTOR, 'input')
    #start_time=times[0]#.send_keys('2011-01-01')
    #start_time.send_keys('2011-01-01')
    date_txt_bg = driver.find_element(By.ID, 'datebox0')
    driver.execute_script("arguments[0].removeAttribute('readonly');", date_txt_bg)
    date_txt_bg.clear()  # 先清除原来的日期值
    date_txt_bg.send_keys(bgdate)
    #date_txt_bg.send_keys(initdate)
    #print('更新开始论文时间：',initdate)

    date_txt_end = driver.find_element(By.ID, 'datebox1')
    driver.execute_script("arguments[0].removeAttribute('readonly');", date_txt_end)
    date_txt_end.clear()  # 先清除原来的日期值
    # date_txt.send_keys('2010-01-01')
    date_txt_end.send_keys(initdate)
    print('更新结束论文时间：', initdate)

    print(times[0].get_attribute('outerHTML'))
    time.sleep(5)
    #start_time = time[0].send_keys('2011-01-01')
    searchbtn = driver.find_element(By.CLASS_NAME, 'btn-search')
    #searchbtn.click()
    driver.execute_script("arguments[0].click();", searchbtn)
    time.sleep(5)
    now_url = driver.current_url #当前页面
    print('主页:',now_url)

    # 只采集学术期刊
    print('只选择学术期刊')
    journal = driver.find_element(By.CSS_SELECTOR, 'a[resource="JOURNAL"]')
    journal.click()
    time.sleep(3)

    main_handle = driver.current_window_handle
    nextbutton=True
    count=1
    page_count=0
    while nextbutton == True:
        nextbutton = False
        print("第%s页" % count)
        if count>=page_count:
            #1、需要输入验证码
            vericodeele = driver.find_elements(By.CLASS_NAME, 'verifycode')
            if len(vericodeele) > 0:
                print('需要验证码')
                nextbutton = True
                continue
            time.sleep(3)
            # 2重新加载、
            reloadele=driver.find_elements(By.ID, 'reload-button')
            if len(reloadele) > 0:
                print('需要重新加载')
                reloadbtn=reloadele[0]
                reloadbtn.click()
                time.sleep(3)
                nextbutton = True
                continue


        try:
            #1、题录全选
            WebDriverWait(driver, 20, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'checkAll')))

            #倒叙排列，点击排序按钮

            #selallclick.click()
            # 开始点击全选
            selallclick = driver.find_element(By.CLASS_NAME, 'checkAll').find_element(By.CSS_SELECTOR, 'input')
            driver.execute_script("arguments[0].click();", selallclick)
            datelist=driver.find_element(By.CLASS_NAME, 'result-table-list').find_elements(By.CLASS_NAME, 'date')
            if (len(datelist)>0) and  count%10==1:
                initdates=datelist[0].get_attribute('innerHTML')
                #print(initdates)
                #initdate=initdates.split(' ')[1]
                initdate = re.findall('\d{4}-\d{2}-\d{2}', initdates)[0]
                print('更新initdate:', initdate)
        except Exception as e:
            driver.quit()
            print('提取题录失败，关闭网页:',e)
            nextbutton = False
            break

        time.sleep(2)

        if ((count%10)==0 and count>page_count):#500下载excel
            print('第%s个表格开始下载'%(count/10))
            downloadexcel(driver)
            windows = driver.window_handles
            print("当前有%s个窗口"%len(windows))
            driver.switch_to.window(main_handle)
            seldeleteall = driver.find_element(By.CLASS_NAME, 'checkcount').find_element(By.CSS_SELECTOR, 'a')
            seldeleteall.click()
            print('下载完成一次===========================\n')
        #2、翻页
        try:
            next_ele=driver.find_element(By.ID, 'Page_next_top')
            #next_ele.click()
            driver.execute_script("arguments[0].click();", next_ele)
            nextbutton = True
            time.sleep(3)
        except Exception as e:
            print("翻页失败",e)
            next_flag=True
            nextbutton = False
            if (count%25)!=0:
               downloadexcel(driver)
        count = count + 1

    driver.quit()



if __name__ == "__main__":
    text = '理工'
    cnkipaperfordatav3(text)
