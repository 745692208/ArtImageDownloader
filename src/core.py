import os
import time
import re
# 第三方库
import pyperclip
import requests #pip install --upgrade urllib3==1.25.2
from concurrent import futures
from multiprocessing import cpu_count

class Core:
    def log(self, message):
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print('[{}]{}'.format(time_date, message))
    
    def __init__(self, log_print=None):
        if log_print: #好像是靠这个捕获打印。然后调用app.py里的函数。
            global print
            print = log_print
        max_workers = cpu_count()*4
        self.session = requests.session()
        # 异步加载，避免GUI卡顿
        self.executor = futures.ThreadPoolExecutor(max_workers)
        #self.executor_video = futures.ThreadPoolExecutor(1)
        self.futures_list = []
        self.b_is_create_folder = True
        self.file_save_dir = ''    #文件保存路径
        
    def run(self):
        # 复制剪切板内容并正则
        #print('Code run')
        clip_content = pyperclip.paste()
        urls = re.findall(r'image_url(.*?),', clip_content)  # 正则表达式解析网页
        if len(urls) == 0:
            self.log('[错误]复制的源码有问题，找不到图片下载地址；')
            return
        try:
            title = re.findall(r'<title>(.*?)</title>', clip_content)[0]  # 正则表达式解析网页
            title = re.sub('[/\:*?"<>|]', "", title)    #去除标题特殊符号
        except:
            self.log('[错误]复制的源码有问题，找不到标题；')
            return
        
        #url处理
        for i,url in enumerate(urls):   
            urls[i] = urls[i].rsplit('"', 1)[0].rsplit('"', 1)[1]
            urls[i] = urls[i].rsplit('?', 1)[0]
        
        # 路径处理
        if self.b_is_create_folder == True: 
            path = os.path.join(self.file_save_dir, title)  #'E:\Python\down\' + 'ArtStation - Mankind&#39;.......'
        else:
            path = self.file_save_dir   #'E:\Python\down\'

        self.log("[正常]解析完成，共计{}张图片；".format(len(urls)))
        #print('run:{}'.format(path))
        self.down_images(urls, path)   # 调用下载图片函数

    def down_images(self, urls, save_path):
        #print('down_images')
        if not os.path.exists(save_path) and self.b_is_create_folder == True:   #创建目录
            os.makedirs(save_path, exist_ok=True)
        for i, url in enumerate(urls):  #循环下载图片
            time.sleep(1)
            self.futures_list.append(self.executor.submit(self.down_image, url, save_path, i))  # 异步加载，避免GUI卡顿
        futures.wait(self.futures_list)
        self.log("[正常]下载任务已完成；")

    def down_image(self, url, save_path, index):
        #print('down_image')
        self.log('[正常]正在下载第{}张，请稍等；'.format(index+1))
        try:
            r = self.session.get(url)  #下载图片
        except:
            self.log('[错误]下载失败，请检查网络设置；')
            return
        
        # 路径处理
        file_name = url.split('/')[-1]  #获取图片名字 gabriel-dias-maia-principal.jpg
        file_name = file_name.rsplit('.', 1)[0] + '-' + str(index) + '.' + file_name.rsplit('.', 1)[1]  #图片名字加index gabriel-dias-maia-principal-0.jpg
        path = os.path.join(save_path, file_name)   #保存路径和文件名字合并
        #print('down_image:{}'.format(path))
        # 写入文件
        with open(path, 'wb') as f:
            f.write(r.content)
        self.log('[完成]{}；'.format(path))
