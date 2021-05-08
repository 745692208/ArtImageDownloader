import os
from concurrent import futures
# 引入Tkinter工具包
from tkinter import Tk, Frame, Label, Button, Scrollbar, Text, Entry
from tkinter import Checkbutton, messagebox, filedialog
from tkinter import TOP, LEFT, BOTH, X, Y, END, IntVar  # BOTTOM
# from tkinter import ttk
import pyperclip

import config
from core import Core

c = config.Config()
conf_dir = c.make_conf_dir('ArtStationImageDownloader')


class App(Frame):
    def app_log(self, value):
        print('log')
        self.logs_box.configure(state="normal")
        self.logs_box.insert(END, value + '\n')
        self.logs_box.see(END)
        self.logs_box.configure(state="disabled")

    def browse(self):
        print('browse')
        dir = os.path.normpath(filedialog.askdirectory())
        if dir:
            config.write_config(conf_dir, 'Base', 'save_path', dir)
            self.save_path = dir
            self.entry_path.delete(0, END)
            self.entry_path.insert(0, self.save_path)

    def check_dir(self):
        if os.path.exists(self.entry_path.get()):
            return True
        else:
            messagebox.showerror("错误", "请输入正确的文件夹路径！")
            return False

    def set_param(self):
        self.core.b_is_create_folder = self.ckbtn_create_folder_var.get()
        self.core.b_is_down_video = self.ckbtn_down_video_var.get()
        self.core.b_is_custom_name = self.ckbtn_custom_name_var.get()
        self.core.entry_path = self.entry_path.get()
        config.write_config(conf_dir, 'Base', 'save_path',
                            self.entry_path.get())

    def get_user_works(self):
        print('get_user_works ui', pyperclip.paste())
        if self.check_dir():
            self.set_param()
            self.core.get_user_works(pyperclip.paste())

    def get_work(self):
        print('get_work ui', pyperclip.paste())
        if self.check_dir():
            self.set_param()
            self.core.get_work(pyperclip.paste())

    def open_folder(self):
        try:
            os.startfile(self.entry_path.get())
        except Exception:
            messagebox.showerror("错误", "请输入正确的文件夹路径！")

    def ckbtn_create_folder_def(self):
        config.write_config(conf_dir, 'Base', 'ckbtn_create_folder_var',
                            str(self.ckbtn_create_folder_var.get()))

    def ckbtn_down_videor_def(self):
        config.write_config(conf_dir, 'Base', 'ckbtn_down_video_var',
                            str(self.ckbtn_down_video_var.get()))

    def ckbtn_custom_name_def(self):
        config.write_config(conf_dir, 'Base', 'ckbtn_custom_name_var',
                            str(self.ckbtn_custom_name_var.get()))

    def createWidgets(self):
        ''' ======== GUI设置 ======== '''
        self.ckbtn_create_folder_var = IntVar()
        try:
            self.ckbtn_create_folder_var.set(int(config.read_config(
                conf_dir, 'Base', 'ckbtn_create_folder_var')))
        except Exception:
            self.ckbtn_create_folder_var.set(0)

        self.ckbtn_down_video_var = IntVar()
        try:
            self.ckbtn_down_video_var.set(int(config.read_config(
                conf_dir, 'Base', 'ckbtn_down_video_var')))
        except Exception:
            self.ckbtn_down_video_var.set(0)

        self.ckbtn_custom_name_var = IntVar()
        try:
            self.ckbtn_custom_name_var.set(int(config.read_config(
                conf_dir, 'Base', 'ckbtn_custom_name_var')))
        except Exception:
            self.ckbtn_custom_name_var.set(1)

        '''控件'''
        self.index1 = Frame(self.root)
        self.index1.pack(side=TOP, fill=X)
        self.index2 = Frame(self.root)
        self.index2.pack(side=TOP, fill=X)
        self.index3 = Frame(self.root)
        self.index3.pack(side=TOP, fill=BOTH, expand=True)

        Label(self.index1, text='Save Path').pack(side=LEFT)
        self.entry_path = Entry(self.index1)
        self.entry_path.pack(side=LEFT, fill=X, expand=True)
        self.entry_path.insert(0, self.save_path)

        Button(self.index1, text='浏览', command=self.browse).pack(side=LEFT)
        Button(self.index1, text='打开文件夹', command=self.open_folder)\
            .pack(side=LEFT)
        Button(
            self.index1, text='爬取单个作品',
            command=lambda: self.executor_ui.submit(self.get_work))\
            .pack(side=LEFT)
        Button(
            self.index1, text='爬取用户',
            command=lambda: self.executor_ui.submit(self.get_user_works))\
            .pack(side=LEFT)
        self.ckbtn_custom_name = Checkbutton(
            self.index1,
            text='自定义命名',
            variable=self.ckbtn_custom_name_var,
            command=self.ckbtn_custom_name_def
        )
        self.ckbtn_custom_name.pack(side=LEFT)
        self.ckbtn_create_folder = Checkbutton(
            self.index1,
            text='创建文件夹',
            variable=self.ckbtn_create_folder_var,
            command=self.ckbtn_create_folder_def
        )
        self.ckbtn_create_folder.pack(side=LEFT)
        self.ckbtn_down_video = Checkbutton(
            self.index1,
            text='下载视频',
            variable=self.ckbtn_down_video_var,
            command=self.ckbtn_down_videor_def
        )
        self.ckbtn_down_video.pack(side=LEFT)
        Label(self.index2, text='Logs:').pack(side=LEFT)

        self.logs_box = Text(self.index3)
        self.logs_box.pack(side=LEFT, fill=BOTH, expand=True)
        self.logs_box.configure(state="disabled")
        self.logs_box.focus()

        self.scrollbar = Scrollbar(self.index3)
        self.scrollbar.pack(side=LEFT, fill=Y)
        self.scrollbar.config(command=self.logs_box.yview)
        self.logs_box.config(yscrollcommand=self.scrollbar.set)

        self.lbl_status = Label(
            self.root, text='使用说明：复制网址然后使用爬取功能即可 By:levosaber')
        self.lbl_status.pack(side=LEFT, fill=X, expand=True)

    def __init__(self, version):
        self.core = Core(self.app_log)  # 可以让core库里调用本app.py的app_log()，不懂啥原理
        master = Tk()
        Frame.__init__(self, master)    # 这个能解决报错，但为什么，不懂。
        master.title("ArtStation Image Downloader " + version)
        self.core = Core()
        self.root = master
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.pack()
        try:
            self.save_path = config.read_config(
                conf_dir, 'Base', 'save_path')
        except Exception:
            self.save_path = ''
        self.createWidgets()


if __name__ == '__main__':
    # 显示GUI
    app = App(version=' GUI Test')
    app.mainloop()
    exit()
