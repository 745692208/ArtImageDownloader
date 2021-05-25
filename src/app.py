import os
import sys
import time
import webbrowser as web
from threading import Timer
from concurrent import futures
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog

import pyperclip  # pip install pyperclip
import config
import core


class App:
    class RepeatingTimer(Timer):
        def run(self):
            while not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                self.finished.wait(self.interval)

    def set_perclip_text(self):
        text = '剪切板：{}'.format(pyperclip.paste()[0:75])
        self.perclip_text.set(text.replace('\n', '').replace('\r', ''))

    def open_folder(self):
        try:
            os.startfile(self.entry_path.get())
        except Exception:
            messagebox.showerror("错误", "请输入正确的文件夹路径！")

    def open_latest_folder(self):
        path = self.cf.load('base', 'save_path')
        if path != '':
            try:
                os.startfile(path)
            except Exception:
                messagebox.showerror("错误", "往期路径不存在！")
        else:
            messagebox.showinfo('无最新保存', '没有保存过作品！')

    def browse(self):
        print('browse')
        dir = os.path.normpath(filedialog.askdirectory())
        if dir != '.':
            self.cf.save('base', 'path', dir)
            self.save_path = dir
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, self.save_path)

    def run(self):
        core.entry_path = self.entry_path.get()
        core.b_is_create_folder = self.is_create_folder.get()
        core.b_is_custom_name = self.is_custom_name.get()
        self.cf.save('base', 'path', self.entry_path.get())
        url = pyperclip.paste()
        if 'youtube' in url:
            self.core_u.down_youtube(url, '', self.entry_path.get())
        elif 'bilibili' in url:
            self.core_u.down_video(url, self.entry_path.get())
        elif 'zbrushcentral' in url:
            self.core_zb.b_is_down_video = self.is_down_video.get()
            self.core_zb.get_work(url)
        elif 'artstation' in url:
            self.core_art.b_is_down_video = self.is_down_video.get()
            if 'artwork' in url:  # 判断是否为单个作品，否则为用户
                self.core_art.get_work(url)
            else:
                self.core_art.get_user_works(url)

    def create_widget(self):
        menubar = tk.Menu(self.app)
        assetWeb = tk.Menu(menubar)
        assetWeb.add_command(
            label='ArtStion',
            command=lambda: web.open('https://www.artstation.com/'))
        assetWeb.add_command(
            label='ZBrushcentral',
            command=lambda: web.open('https://www.zbrushcentral.com/'))
        assetWeb.add_command(
            label='YouTube',
            command=lambda: web.open('https://www.youtube.com/'))
        assetWeb.add_command(
            label='BiliBili',
            command=lambda: web.open('https://www.bilibili.com/'))
        menubar.add_command(
            label='关于',
            command=lambda: web.open(
                'https://github.com/745692208/MultipleDownloaders'))
        menubar.add_cascade(label='资源网站', menu=assetWeb)
        menubar.add_command(
            label='使用帮助',
            command=lambda: messagebox.showinfo(
                '使用帮助', self.helpText))
        self.app['menu'] = menubar
        # 1 第一行 标签容器 创建标签
        fTab = tk.Frame(self.app)
        fTab.pack(side='top', fill='x')
        # 2 第二行 save
        fSave = tk.Frame(self.app)
        fSave.pack(side='top', fill='x')
        ttk.Label(fSave, text='Save Path').pack(side='left')
        self.entry_path = ttk.Entry(fSave)
        self.entry_path.pack(side='left', fill='x', expand=True)
        self.entry_path.insert(0, self.save_path)

        ttk.Button(fSave, text='浏览', command=self.browse).pack(side='left')
        ttk.Button(fSave, text='打开文件夹', command=self.open_folder)\
            .pack(side='left')
        ttk.Button(
            fSave, text='打开最近保存文件夹',
            command=self.open_latest_folder)\
            .pack(side='left')

        fSave_2 = tk.Frame(self.app)
        fSave_2.pack(side='top', fill='x')

        self.is_custom_name = tk.IntVar()
        self.is_custom_name.set(
            self.cf.load('base', 'is_custom_name', 1))
        ttk.Checkbutton(
            fSave_2,
            text='自定义命名',
            variable=self.is_custom_name,
            command=lambda: self.cf.save(
                'base', 'is_custom_name',
                str(self.is_custom_name.get())
            )
        ).pack(side='left')

        self.is_create_folder = tk.IntVar()
        self.is_create_folder.set(
            self.cf.load('base', 'is_create_folder', 1))
        ttk.Checkbutton(
            fSave_2,
            text='创建文件夹',
            variable=self.is_create_folder,
            command=lambda: self.cf.save(
                'base', 'is_create_folder',
                str(self.is_create_folder.get())
            )
        ).pack(side='left')
        self.is_down_video = tk.IntVar()
        self.is_down_video.set(self.cf.load(
            'base', 'is_down_video', 1))
        ttk.Checkbutton(
            fSave_2,
            text='下载视频',
            variable=self.is_down_video,
            command=lambda: self.cf.save(
                'base', 'is_down_video',
                str(self.is_down_video.get())
            )
        ).pack(side='left')
        ttk.Button(
            fSave_2,
            text='自动分析链接并爬取',
            command=lambda: self.executor_ui.submit(
                self.run)
        ).pack(side='left', fill='x', expand=1)
        # 4 第四行 Logs界面
        self.fLogs = ttk.LabelFrame(self.app, text='Logs')
        self.fLogs.pack(side='top', fill='both', expand=1)

        self.perclip_text = tk.StringVar()
        ttk.Label(self.fLogs, anchor='w', textvariable=self.perclip_text)\
            .pack(side='top', fill='x')
        fLogs_box = ttk.Frame(self.fLogs)
        fLogs_box.pack(side='left', fill='both', expand=1)
        self.logs_box = tk.Text(fLogs_box)
        self.logs_box.pack(side='left', fill='both', expand=1)
        self.logs_box.configure(state="disabled")
        self.logs_box.focus()
        # Logs界面 滚动条
        scrollbar = ttk.Scrollbar(fLogs_box)
        scrollbar.pack(side='left', fill='y')
        scrollbar.config(command=self.logs_box.yview)
        self.logs_box.config(yscrollcommand=scrollbar.set)

    def app_log(self, value):
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = '[{}]{}'.format(time_date, value)
        self.logs_box.configure(state="normal")
        self.logs_box.insert('end', value + '\n')
        self.logs_box.see('end')
        self.logs_box.configure(state="disabled")

    def __init__(self, title, ver, suffix):
        self.helpText = '\1、网址复制到剪切板，会自动读取并分析和爬取资源。\
            \n2、下载视频选项只影响A站和ZB站的资源爬取。\
            \n3、目前支持A站、ZB站、B站的资源下载。'
        self.cf = config.Config('MultipleDownloaders', 0, './test/')
        core.cf = self.cf
        core.Utils(self.app_log)
        self.core_zb = core.ZBrush()
        self.core_art = core.ArtStation()
        self.core_u = core.Utils()
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.app = tk.Tk()
        self.app.title('{} {} {}'.format(title, ver, suffix))
        # 变量
        self.ftab_list = []
        self.save_path = self.cf.load('base', 'path')
        self.tab_index = tk.IntVar()
        self.tab_index.set(self.cf.load('base', 'tab_index', 0))
        # 运行
        self.create_widget()
        # self.changeTab()
        self.t = self.RepeatingTimer(1, self.set_perclip_text)
        self.t.start()


if __name__ == '__main__':
    app = App('Test', '', '')
    app.app.mainloop()
    app.t.cancel()
    sys.exit()
