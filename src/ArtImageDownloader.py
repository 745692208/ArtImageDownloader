#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import os
import sys
from threading import Timer
from concurrent import futures
import configparser
import core
import pyperclip  # pip install pyperclip
import time

ui_name = 'Art Image Downloader'
ui_version = '1.0 by levosaber'
saveName = ['2D', '3D', '3D角色', '3D场景', '3D生物', '其它']

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


class App:
    class RepeatingTimer(Timer):
        def run(self):
            while not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                self.finished.wait(self.interval)

    def set_perclipText(self):
        text = '剪切板：{}'.format(pyperclip.paste()[0:75])
        self.perclipText.set(text.replace('\n', '').replace('\r', ''))

    def on_OpenConfig(self):
        print('on_OpenConfig')
        path = os.path.dirname(os.path.realpath(__file__))
        path = path + '/' + ui_name + '.ini'
        os.startfile(path)

    def on_SaveConfig(self):
        print('on_SaveConfig')
        self.cf.save('a', 'savePath', self.savePath)
        self.cf.save('a', 'isCustomName', str(self.isCustomName.get()))
        self.cf.save('a', 'isCreateFolder', str(self.isCreateFolder.get()))
        self.cf.save('a', 'isDownloadVideo', str(self.isDownloadVideo.get()))
        self.cf.save('a', 'lastSavePath', self.lastSavePath)
        self.cf.save('a', 'saveName', ','.join(saveName))

    def loadConfig(self):
        load = self.cf.load('a', 'saveName')
        if load != '':
            self.saveName = load.split(',')
        self.savePath.set(self.cf.load('a', 'savePath', 'D:/Test'))
        self.isCustomName.set(int(self.cf.load('a', 'isCustomName', '1')))
        self.isDownloadVideo.set(int(self.cf.load('a', 'isCreateFolder', '1')))
        self.isCreateFolder.set(int(self.cf.load('a', 'isDownloadVideo', '1')))
        self.lastSavePath = self.cf.load('a', 'lastSavePath', 'D:/Test')

    def on_OpenLastFolder(self):
        print('on_OpenLastFolder', self.lastSavePath)
        os.startfile(self.lastSavePath)

    def on_OpenFolder(self, name):
        print('on_OpenFolder', name)
        os.startfile(os.path.join(self.savePath.get(), name))

    def on_Download(self, name):
        print('on_Download', name)
        core.savePath = self.savePath.get()
        core.b_is_create_folder = self.isCreateFolder.get()
        core.b_is_custom_name = self.isCustomName.get()
        url = pyperclip.paste()
        if 'youtube' in url:
            self.core_u.down_youtube(url, '', self.savePath.get())
        elif 'bilibili' in url:
            self.core_u.down_video(url, self.savePath.get())
        elif 'zbrushcentral' in url:
            self.core_zb.b_is_down_video = self.isDownloadVideo.get()
            self.core_zb.get_work(url)
        elif 'artstation' in url:
            self.core_art.b_is_down_video = self.isDownloadVideo.get()
            if 'artwork' in url:  # 判断是否为单个作品，否则为用户
                self.core_art.get_work(url)
            else:
                self.core_art.get_user_works(url)

    def on_Browse(self):
        print('on_Browse')
        dir = os.path.normpath(filedialog.askdirectory())
        if dir != '.':
            self.savePath.set(dir)

    def createItem(self, ui_main, name):
        print('createItem')
        f = ttk.Frame(ui_main)
        f.pack(fill="x", side="top")
        a = ttk.Label(f, anchor="center", text=name, width="15")
        a.pack(side="left")
        a = ttk.Button(f, text="打开文件夹")
        a.configure(command=lambda: self.on_OpenFolder(name))
        a.pack(side="left")
        a = ttk.Button(f, text="下载到此处")
        a.configure(command=lambda: self.on_Download(name))
        a.pack(expand="true", fill="x")

    def app_log(self, value):
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = '[{}]{}'.format(time_date, value)
        self.ui_logs_text.configure(state="normal")
        self.ui_logs_text.insert('end', value + '\n')
        self.ui_logs_text.see('end')
        self.ui_logs_text.configure(state="disabled")

    def __init__(self, master=None):
        self.cf = Config(ui_name)
        core.cf = self.cf
        core.Utils(self.app_log)
        self.core_zb = core.ZBrush()
        self.core_art = core.ArtStation()
        self.core_u = core.Utils()
        self.executor_ui = futures.ThreadPoolExecutor(1)
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
        self.loadConfig()
        # 01 options -----------------------------------
        ui_f0 = ttk.Frame(ui_main)
        ui_f0.pack(fill="x")
        a = ttk.Button(ui_f0, text="Open.ini", command=self.on_OpenConfig)
        a.pack(side='left', expand="true", fill="x")
        a = ttk.Button(ui_f0, text="Save.ini", command=self.on_SaveConfig)
        a.pack(side='left', expand="true", fill="x")
        # 02 options -----------------------------------
        ui_f1 = ttk.Frame(ui_main)
        ui_f1.pack(fill="x", side="top")
        a = ttk.Label(ui_f1, justify="left", text="Save Path：")
        a.pack(side="left")
        a = ttk.Entry(ui_f1, textvariable=self.savePath)
        a.pack(expand="true", fill="x", side="left")
        a = ttk.Button(ui_f1, text="浏览", command=self.on_Browse)
        a.pack(side="left")
        # 03 options -----------------------------------
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
        a.pack(expand="true", fill="x", side="top")
        a = ttk.Separator(ui_main, orient="horizontal")
        a.pack(fill="x", pady="2")
        # 04 item -----------------------------------
        for name in saveName:
            self.createItem(ui_main, name)
        a = ttk.Separator(ui_main, orient="horizontal")
        a.pack(fill="x", pady="2")
        # 05 logs -----------------------------------
        ui_logs = ttk.Frame(ui_main)
        ui_logs.pack(expand="true", fill="both", side="top")
        a = ttk.Label(ui_logs, justify="left", textvariable=self.perclipText)
        a.pack(expand="false", fill="x", side="top")
        self.ui_logs_text = tk.Text(ui_logs, state="disabled")
        self.ui_logs_text.configure(height=10, state="disabled", width="50")
        self.ui_logs_text.pack(expand="true", fill="both", side="left")
        # Main widget
        self.mainwindow = ui_main
        self.t = self.RepeatingTimer(1, self.set_perclipText)
        self.t.start()

    def run(self):
        self.mainwindow.mainloop()
        self.t.cancel()
        sys.exit()


if __name__ == "__main__":
    app = App()
    app.run()
