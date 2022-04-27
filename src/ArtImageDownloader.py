import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog

import os
import re
import sys
import time
import configparser
import webbrowser as web

from threading import Timer, Thread
from concurrent import futures
from multiprocessing import cpu_count

import pyperclip  # pip install pyperclip
import requests  # pip install --upgrade urllib3==1.25.2

# =============================== 全局变量 ===============================
ui_name = 'Art Image Downloader'
ui_version = '1.0.220427 by levosaber'
saveName = ['2D', '2D角色', '2D生物', '2D场景', '2D卡通',
            '3D', '3D写实', '3D卡通', '3D手绘', '3D素体',
            '3D角色-现代', '3D角色-古代', '3D角色-未来', '3D生物', 'x',
            '3D场景', '3D道具', '3D载具', '其它',  'x']
rowNum = 5
h = 15
w = 100

# =============================== Config ===============================


class Config:

    def load(self, field, key, *failValue):
        '''读取
        :param *failValue, None, 读取失败后，返回的值。默认返回'';'''
        if len(failValue) == 0:
            failValue = ''
        else:
            failValue = failValue[0]
        cf = configparser.ConfigParser()
        try:
            cf.read(self.path, encoding="utf-8")
            if field in cf:
                result = cf.get(field, key)
            else:
                return failValue
        except Exception:
            return failValue
        return result

    def save(self, field, key, value):
        '''保存'''
        cf = configparser.ConfigParser()
        try:
            cf.read(self.path, encoding="utf-8")
            if field not in cf:
                cf.add_section(field)
            cf.set(field, key, value)
            cf.write(open(self.path, "w", encoding="utf-8"))
        except Exception:
            return False
        return True

    def __init__(self, name):
        '''Config使用整合，通过设置ini文件路径，使用save、load方法，即可便捷使用。
        :param name, str, 默认文件夹和ini的名字。'''
        self.cf = configparser.ConfigParser()
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.path = self.path + '/' + name + '.ini'
        print(self.path)


# =============================== Core ===============================
class Core:

    def __init__(self, app_print=None, cf=None):
        self.app_print = app_print
        self.cf = cf
        self.executor = futures.ThreadPoolExecutor(cpu_count() * 4)
        self.executor_video = futures.ThreadPoolExecutor(1)
        self.session = requests.session()
        self.isCustomName = True
        self.isCreateFolder = True
        self.isDownloadVideo = False
        self.savePath = ''
        self.lastSavePath = ''

    # 工具 ------------------
    def print_log(self, str):
        if self.app_print:
            self.app_print(str)
        else:
            print(str)

    def session_get(self, url):
        try:
            r = self.session.get(url)
            self.print_log('网络连接成功，正在分析数据，请稍等...')
            return r
        except Exception as e:
            self.print_log('网络连接失败，错误：{};'.format(e))
            return

    def down_file(self, url, file_name, save_path):  # 下载图片
        '''下载输入的网址文件，并对其命名，保存到指定位置。
        :param url, str, 输入网页地址，如：https://cdna.artstation.com/p/1.jpg ;
        :param file_name, str, 文件保存名字，比如：awaw-5X9mYA-1.jpg ;
        :param save_path. str, 保存地址，比如：E:/asd '''
        r = self.session.get(url)  # 下载图片
        path = os.path.join(save_path, file_name)  # 保存路径和文件名字合并
        with open(path, 'wb') as f:
            f.write(r.content)

    def make_name(slef, name, index, format):
        '''通过输入的参数，合成名字，name1-name2-index.format
        :param index, int, 请输入0开始的，因为会自动+1'''
        return '{}-{}.{}'.format(name, index + 1, format)

    def make_save_path(slef, name):
        '''输入名字并判断是否需要创建文件夹，最终制作保存路径'''
        if slef.isCreateFolder:
            return os.path.join(slef.savePath, name)
        return slef.savePath

    def check_make_dir(self, path):
        '''检查输入的路径是否有效，无效则尝试创建文件夹，最终成功后保存路径'''
        self.lastSavePath = path
        self.cf.save('a', 'lastSavePath', path)
        if os.path.exists(path):
            return True
        else:
            try:
                os.makedirs(path, exist_ok=True)
                self.print_log('保存地址：{}'.format(path))
                return True
            except Exception as e:
                messagebox.showerror("错误", "请输入正确的文件夹路径！")
                self.print_log(e)
                return False

    # A站 ------------------
    def get_user_works(self, url):  # 获取用户的所有作品
        '''
        :param url, str, 网页地址，比如：https://www.artstation.com/pouria_roshan
        '''
        self.print_log('分析中，请不要进行操作...')
        username = url.split('/')[-1]
        data = []
        page = 0  # 一页最大data数为50，0~49，page为1起步
        while True:
            page += 1
            url = 'https://www.artstation.com/users/{}/projects.json?page={}'\
                .format(username, page)
            j = self.session_get(url).json()
            total_count = int(j['total_count'])
            data += j['data']
            if page > total_count / 50:
                break
        self.print_log('作者：{}，共计{}个作品，现进行作品分析... '.format(username, len(data)))
        futures_list = []
        for wrok in data:
            futures_list.append(
                self.executor.submit(self.get_work, wrok['permalink']))
        futures.wait(futures_list)
        self.print_log("爬取用户作品的下载任务已全部完成；\n")

    def get_work(self, url):
        '''
        获取单独作品
        :param url, str, 网页地址，比如：https://www.artstation.com/artwork/5X9mYA ;'''
        # 获取json资产数据
        self.print_log('分析网址：{}，请稍等...'.format(url))
        work_id = url.rsplit('/', 1)[1]
        url = 'https://www.artstation.com/projects/{}.json'.format(work_id)
        j = self.session_get(url).json()
        assets = j['assets']  # 获取资产
        for i, asset in enumerate(assets):  # 删除多余资产
            if asset['asset_type'] == 'cover':
                del assets[i]
        # 创建文件夹
        title = j['title'].strip()  # 获取标题
        title = re.sub(r'[/\:*?"<>|]', "", title)  # 去除标题特殊符号
        work_name = self.custom_name(j, work_id)  # pouria_roshan-5X9mYA
        path = self.make_save_path(title)  # D:\python\down\Buttercup
        self.check_make_dir(path)
        # 3 资产数据分析
        self.print_log('分析完毕，作品：{}，现进行下载...'.format(j['title'].strip()))
        futures_list = []
        for i, asset in enumerate(assets):
            if asset['asset_type'] == 'image':
                url = asset['image_url'].rsplit('?', 1)[0]
                file_format = url.rsplit('.', 1)[1]  # .jpg
                name = self.make_name(work_name, i, file_format)
                self.print_log('图片：{}'.format(url))
                futures_list.append(
                    self.executor.submit(self.down_file, url, name, path))
            elif asset['asset_type'] == 'video_clip' and self.isDownloadVideo:
                url = re.findall(r"src='(.*?)'", asset['player_embedded'])[0]
                r = self.session_get(url)
                source_media = re.findall(r'src="(.*?)" type=', r.text)[0]
                file_format = source_media.rsplit('.', 1)[1]  # .jpg
                name = self.make_name(work_name, i, file_format)
                self.print_log('视频：{}'.format(source_media))
                futures_list.append(
                    self.executor.submit(self.down_file, source_media, name,
                                         path))
        futures.wait(futures_list)
        self.print_log("下载任务已完成；\n")

    def custom_name(self, j, file_name):
        if self.isCustomName:
            username = j['user']['username']
            work_id = j['hash_id']
            file_name = file_name.rsplit('.', 1)
            return '{}-{}'.format(username, work_id)
        else:
            return file_name

    # zb ------------------
    def zb_get_work(self, url):
        self.print_log("ZB下载任务开始中，亲稍等，url：{}".format(url))
        r = self.session_get(url).text
        # 图片
        urls = re.findall(r'<img src="//(.*?).jpeg"', r)
        work_name = '{}-{}'.format(
            url.rsplit('/', 2)[1],
            url.rsplit('/', 2)[2])  # SwordGirl-402912
        path = self.make_save_path(work_name)
        self.check_make_dir(path)
        futures_list = []
        self.print_log('开始咯')
        for i, down_url in enumerate(urls):
            down_url = r'https://' + down_url + '.jpeg'
            name = self.make_name(work_name, i, 'jpeg')
            futures_list.append(
                self.executor.submit(self.down_file, down_url, name, path))
        # 视频
        if self.isDownloadVideo:
            urls_video = re.findall(r'www(.*?)mp4', r)
            work_name = work_name + '_video'
            for i, video_url in enumerate(urls_video):
                video_url = 'https://www' + video_url + 'mp4'
                name = self.make_name(work_name, i, 'mp4')
                self.print_log('这是个视频，下载比较忙，亲耐心等候。')
                futures_list.append(
                    self.executor.submit(self.down_file, video_url, name,
                                         path))
        futures.wait(futures_list)
        self.print_log("[正常]下载任务已完成；\n")


# =============================== App ===============================
class App:

    class RepeatingTimer(Timer):

        def run(self):
            while not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                self.finished.wait(self.interval)

    def run_in_thread(fun):

        def wrapper(*args, **kwargs):
            thread = Thread(target=fun, args=args, kwargs=kwargs)
            thread.start()
            return thread

        return wrapper

    def set_perclipText(self):
        text = '剪切板：{}'.format(pyperclip.paste()[0:75])
        self.perclipText.set(text.replace('\n', '').replace('\r', ''))

    def on_OpenConfig(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = path + '/' + ui_name + '.ini'
        try:
            os.startfile(path)
        except Exception:
            self.app_log('没有ini文件，请先保存ini。')

    def SaveConfig(self):
        self.cf.save('a', 'savePath', self.savePath.get())
        self.cf.save('a', 'isCustomName', str(self.isCustomName.get()))
        self.cf.save('a', 'isCreateFolder', str(self.isCreateFolder.get()))
        self.cf.save('a', 'isDownloadVideo', str(self.isDownloadVideo.get()))
        self.cf.save('ui', 'saveName', ','.join(self.saveName))
        self.cf.save('ui', 'rowNum', str(self.rowNum))
        self.cf.save('ui', 'h', str(self.h))
        self.cf.save('ui', 'w', str(self.w))

    def loadConfig(self):
        self.rowNum = int(self.cf.load('ui', 'rowNum', str(rowNum)))
        self.h = int(self.cf.load('ui', 'h', str(h)))
        self.w = int(self.cf.load('ui', 'w', str(w)))
        load = self.cf.load('ui', 'saveName')
        if load != '':
            self.saveName = load.split(',')
        self.savePath.set(self.cf.load('a', 'savePath', 'D:/Test'))
        self.isCustomName.set(int(self.cf.load('a', 'isCustomName', '1')))
        self.isCreateFolder.set(int(self.cf.load('a', 'isCreateFolder', '0')))
        self.isDownloadVideo.set(int(self.cf.load('a', 'isDownloadVideo',
                                                  '1')))
        self.c.lastSavePath = self.cf.load('a', 'lastSavePath', 'D:/Test')

    def on_OpenLastFolder(self):
        os.startfile(self.c.lastSavePath)
        self.app_log('打开最近保存文件夹：{}'.format(self.c.lastSavePath))

    def on_OpenFolder(self, name=''):
        path = os.path.join(self.savePath.get(), name)
        os.startfile(path)
        self.app_log('打开文件夹：{}'.format(path))

    def on_Browse(self):
        dir = os.path.normpath(filedialog.askdirectory())
        if dir != '.':
            self.savePath.set(dir)
            self.SaveConfig()

    def app_log(self, value):
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = '[{}]{}'.format(time_date, value)
        self.ui_logs_text.configure(state="normal")
        self.ui_logs_text.insert('end', value + '\n')
        self.ui_logs_text.see('end')
        self.ui_logs_text.configure(state="disabled")

    @run_in_thread
    def on_Download(self, name):
        self.SaveConfig()
        url = pyperclip.paste()
        self.c.isCustomName = self.isCustomName.get()
        self.c.isCreateFolder = self.isCreateFolder.get()
        self.c.isDownloadVideo = self.isDownloadVideo.get()
        self.c.savePath = os.path.join(self.savePath.get(), name)
        if 'zbrushcentral' in url:
            self.c.get_work(url)
        elif 'artstation' in url:
            if 'artwork' in url:  # 判断是否为单个作品，否则为用户
                self.c.get_work(url)
            else:
                self.c.get_user_works(url)
        else:
            self.app_log('剪切板中信息有误，无法爬取数据。')

    def createItem(self, f, name, i):
        r = int(i / self.rowNum)
        c = i - r * self.rowNum
        a = ttk.Button(f, text=name)
        a.configure(command=lambda: self.on_Download(name))
        a.grid(column=c, row=r, padx=1, pady=1)

    def createUI(self, master=None):
        # build ui
        ui_main = tk.Tk() if master is None else tk.Toplevel(master)
        ui_main.title('{} {} '.format(ui_name, ui_version))
        # build variable
        self.savePath = tk.StringVar(value='D:/Test')
        self.isCustomName = tk.IntVar(value=1)
        self.isDownloadVideo = tk.IntVar(value=1)
        self.isCreateFolder = tk.IntVar(value=1)
        self.lastSavePath = ''
        self.perclipText = tk.StringVar(value='')
        self.saveName = saveName
        self.loadConfig()
        # 00 menu -----------------------------------
        menubar = tk.Menu(ui_main)
        options = tk.Menu(menubar, tearoff=0)
        options.add_command(label='Open.ini', command=self.on_OpenConfig)
        options.add_command(label='Save.ini', command=self.SaveConfig)
        menubar.add_cascade(label='Options', menu=options)
        # about
        about = tk.Menu(menubar, tearoff=0)
        a = 'https://github.com/745692208/ArtImageDownloader'
        about.add_command(label='Github', command=lambda: web.open(a))
        about.add_separator()
        a = 'https://www.artstation.com/'
        about.add_command(label='ArtStion', command=lambda: web.open(a))
        a = 'https://www.zbrushcentral.com/'
        about.add_command(label='ZBrushcentral', command=lambda: web.open(a))
        menubar.add_cascade(label='About', menu=about)
        ui_main['menu'] = menubar
        # 01 options -----------------------------------
        ui_f1 = ttk.Frame(ui_main)
        ui_f1.pack(fill="x", side="top")
        a = ttk.Label(ui_f1, justify="left", text="Save Path：")
        a.pack(side="left")
        a = ttk.Entry(ui_f1, textvariable=self.savePath)
        a.pack(expand="true", fill="x", side="left")
        a = ttk.Button(ui_f1, text="浏览", command=self.on_Browse)
        a.pack(side="left")
        # btn 打开文件夹-----
        a = ttk.Button(ui_f1, text="打开文件夹", command=self.on_OpenFolder)
        a.pack(side="left")
        # 02 options -----------------------------------
        ui_f2 = ttk.Frame(ui_main)
        ui_f2.pack(fill="x", side="top")
        # cb 自定义命名-----
        a = ttk.Checkbutton(ui_f2, text="自定义命名", variable=self.isCustomName)
        a.pack(side="left")
        # cb 创建文件夹-----
        a = ttk.Checkbutton(ui_f2, text="创建文件夹", variable=self.isCreateFolder)
        a.pack(side="left")
        # cb 下载视频-----
        a = ttk.Checkbutton(ui_f2, text="下载视频", variable=self.isDownloadVideo)
        a.pack(side="left")
        # btn 打开最近保存文件夹-----
        a = ttk.Button(ui_f2, text="打开最近保存文件夹", command=self.on_OpenLastFolder)
        a.pack(expand="true", fill="x", side="left")
        # 03 item -----------------------------------
        f = ttk.LabelFrame(ui_main, text='点击按钮下载到指定文件夹')
        f.pack(fill="x", side="top")
        for i, name in enumerate(self.saveName):
            self.createItem(f, name, i)
        # 04 logs -----------------------------------
        ui_logs = ttk.Frame(ui_main)
        ui_logs.pack(expand="true", fill="both", side="top")
        a = ttk.Label(ui_logs, justify="left", textvariable=self.perclipText)
        a.pack(expand="false", fill="x", side="top")
        self.ui_logs_text = tk.Text(ui_logs, state="disabled")
        self.ui_logs_text.configure(height=self.h,
                                    state="disabled",
                                    width=self.w)
        self.ui_logs_text.pack(expand="true", fill="both", side="left")
        # Main widget
        self.mainwindow = ui_main

    def __init__(self):
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.cf = Config(ui_name)
        self.c = Core(self.app_log, self.cf)
        self.createUI()
        self.t = self.RepeatingTimer(1, self.set_perclipText)
        self.t.start()


if __name__ == "__main__":
    app = App()
    app.mainwindow.mainloop()
    app.t.cancel()
    sys.exit()
