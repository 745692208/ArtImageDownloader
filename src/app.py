import os
import sys
import re
from threading import Timer
from concurrent import futures
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import StringVar, messagebox, filedialog

import pyperclip
import requests   # pip install --upgrade urllib3==1.25.2
import config


class App:
    def __init__(self, title, ver, suffix) -> None:
        self.ftab_list = []
        self.cf = config.Config('ArtDown', True, './test/')
        # 创建GUI
        self.app = tk.Tk()
        self.app.title('{} {} {}'.format(title, ver, suffix))
        self.create_widget()
        self.changeTab(0)
        self.t = self.RepeatingTimer(1, self.set_perclip_text)
        self.t.start()
        pass

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

    def browse(self):
        print('browse')
        dir = os.path.normpath(filedialog.askdirectory())
        if dir != '.':
            # config.write_config(conf_dir, 'Base', 'save_path', dir)
            self.save_path = dir
            self.entry_path.delete(0, 'end')
            self.entry_path.insert(0, self.save_path)

    def check_dir(self):
        if os.path.exists(self.entry_path.get()):
            return True
        else:
            try:
                os.makedirs(self.entry_path.get(), exist_ok=True)
                return True
            except Exception:
                messagebox.showerror("错误", "请输入正确的文件夹路径！")
                return False

    def changeTab(self, index):
        print(index)
        self.fLogs.pack_forget()
        for ftab in self.ftab_list:
            ftab.pack_forget()
        self.ftab_list[index].pack(fill='x')
        self.fLogs.pack(side='top', fill='both', expand=1)

    def ckbtn_save():
        pass

    def create_widget(self):
        print('create_widget')
        # 1 第一行 标签容器 创建标签 这里存在bug
        fTab = tk.Frame(self.app)
        fTab.pack(side='top', fill='x')
        tab_index = tk.IntVar()
        tab_index.set(0)
        tk.Radiobutton(
            fTab, text="ArtStation", indicatoron=1, value=0,
            variable=tab_index, command=lambda: self.changeTab(0))\
            .pack(side='left')
        tk.Radiobutton(
            fTab, text="ZBrushCentral", indicatoron=1, value=1,
            variable=tab_index, command=lambda: self.changeTab(1))\
            .pack(side='left')

        # 2 第二行 save
        fSave = tk.Frame(self.app)
        fSave.pack(side='top', fill='x')
        tk.Label(fSave, text='Save Path').pack(side='left')
        self.entry_path = tk.Entry(fSave)
        self.entry_path.pack(side='left', fill='x', expand=True)
        # self.entry_path.insert(0, self.save_path)

        ttk.Button(fSave, text='浏览', command=self.browse).pack(side='left')
        ttk.Button(fSave, text='打开文件夹', command=self.open_folder)\
            .pack(side='left')

        # 3 第三行
        # ArtStation页面
        self.fTool_art = tk.LabelFrame(self.app, text='ArtStation')
        self.fTool_art.pack(side='top', fill='x')
        self.ftab_list.append(self.fTool_art)

        self.ckbtn_custom_name_var = tk.IntVar()
        self.ckbtn_custom_name = tk.Checkbutton(
            self.fTool_art,
            text='自定义命名',
            variable=self.ckbtn_custom_name_var,
            command=lambda: self.cf.save(
                'art', 'ckbtn_custom_name',
                self.ckbtn_custom_name_var.get()
            )
        )
        self.ckbtn_custom_name.pack(side='left')
        self.ckbtn_down_video_var = tk.IntVar()
        self.ckbtn_down_video = tk.Checkbutton(
            self.fTool_art,
            text='下载视频',
            variable=self.ckbtn_down_video_var,
            command=lambda: self.cf.save(
                'art', 'ckbtn_down_video',
                self.ckbtn_down_video_var.get()
            )
        )
        self.ckbtn_down_video.pack(side='left')
        self.ckbtn_create_folder_var = tk.IntVar()
        self.ckbtn_create_folder = tk.Checkbutton(
            self.fTool_art,
            text='创建文件夹',
            variable=self.ckbtn_create_folder_var,
            command=lambda: self.cf.save(
                'art', 'ckbtn_create_folder',
                self.ckbtn_create_folder_var.get()
            )
        )
        self.ckbtn_create_folder.pack(side='left')

        ttk.Button(
            self.fTool_art, text='爬取单个作品',
            command=lambda: self.executor_ui.submit(self.get_work))\
            .pack(side='left')
        ttk.Button(
            self.fTool_art, text='爬取用户',
            command=lambda: self.executor_ui.submit(self.get_user_works))\
            .pack(side='left')
        ttk.Button(
            self.fTool_art, text='打开最新保存文件夹',
            command=self.open_folder)\
            .pack(side='left', fill='x', expand=True)

        # ZBrushCentral界面
        self.fTool_zb = tk.LabelFrame(self.app, text='ZBrushCentral')
        self.fTool_zb.pack(side='top', fill='x')
        self.ftab_list.append(self.fTool_zb)
        ttk.Button(self.fTool_zb, text='text1').pack()

        # 4 第四行 Logs界面
        self.fLogs = tk.LabelFrame(self.app, text='Logs')
        self.fLogs.pack(side='top', fill='x', expand=1)
        self.perclip_text = tk.StringVar()
        tk.Label(self.fLogs, anchor='w', textvariable=self.perclip_text)\
            .pack(side='top', fill='x', expand=1)
        self.logs_box = tk.Text(self.fLogs)
        self.logs_box.pack(side='top', fill='both', expand=1)     # left
        self.logs_box.configure(state="disabled")
        self.logs_box.focus()
        # Logs界面 滚动条
        self.scrollbar = tk.Scrollbar(self.fLogs)
        self.scrollbar.pack(side='top', fill='y')
        self.scrollbar.config(command=self.logs_box.yview)
        self.logs_box.config(yscrollcommand=self.scrollbar.set)


if __name__ == '__main__':
    app = App('GUI Test', '2.0.0', '')
    app.app.mainloop()
    app.t.cancel()
    sys.exit()
