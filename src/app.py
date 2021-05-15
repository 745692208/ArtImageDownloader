import os
import time
from concurrent import futures
from threading import Timer
from tkinter import StringVar, Tk, Frame, Label, Button, Scrollbar, Text, Entry
from tkinter import Checkbutton, messagebox, filedialog
from tkinter import TOP, LEFT, BOTH, X, Y, END, IntVar  # BOTTOM

import pyperclip
import config
from core import Core

c = config.Config()
conf_dir = c.make_conf_dir('ArtStationImageDownloader')


class App(Frame):
    def app_log(self, value):
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = '[{}]{}'.format(time_date, value)
        self.logs_box.configure(state="normal")
        self.logs_box.insert(END, value + '\n')
        self.logs_box.see(END)
        self.logs_box.configure(state="disabled")

    def browse(self):
        print('browse')
        dir = os.path.normpath(filedialog.askdirectory())
        if dir != '.':
            config.write_config(conf_dir, 'Base', 'save_path', dir)
            self.save_path = dir
            self.entry_path.delete(0, END)
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

    def open_latest_folder(self):
        path = self.core.save_path
        if path != '':
            os.startfile(path)
        else:
            messagebox.showinfo('无最新保存', '本次运行没有保存过作品！')

    # ini保存
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
            self.ckbtn_create_folder_var.set(1)

        self.ckbtn_down_video_var = IntVar()
        try:
            self.ckbtn_down_video_var.set(int(config.read_config(
                conf_dir, 'Base', 'ckbtn_down_video_var')))
        except Exception:
            self.ckbtn_down_video_var.set(1)

        self.ckbtn_custom_name_var = IntVar()
        try:
            self.ckbtn_custom_name_var.set(int(config.read_config(
                conf_dir, 'Base', 'ckbtn_custom_name_var')))
        except Exception:
            self.ckbtn_custom_name_var.set(1)
        # 变量
        self.perclip_text = StringVar()

        '''控件'''
        self.index1 = Frame(self.root)
        self.index1.pack(side=TOP, fill=X)
        self.index2 = Frame(self.root)
        self.index2.pack(side=TOP, fill=X)
        self.f_logs = Frame(self.root)
        self.f_logs.pack(side=TOP, fill=X)
        self.index3 = Frame(self.root)
        self.index3.pack(side=TOP, fill=BOTH, expand=True)
        # 第一行
        Label(self.index1, text='Save Path').pack(side=LEFT)
        self.entry_path = Entry(self.index1)
        self.entry_path.pack(side=LEFT, fill=X, expand=True)
        self.entry_path.insert(0, self.save_path)

        Button(self.index1, text='浏览', command=self.browse).pack(side=LEFT)
        Button(self.index1, text='打开文件夹', command=self.open_folder)\
            .pack(side=LEFT)
        # 第二行
        self.ckbtn_custom_name = Checkbutton(
            self.index2,
            text='自定义命名',
            variable=self.ckbtn_custom_name_var,
            command=self.ckbtn_custom_name_def
        )
        self.ckbtn_custom_name.pack(side=LEFT)
        self.ckbtn_create_folder = Checkbutton(
            self.index2,
            text='创建文件夹',
            variable=self.ckbtn_create_folder_var,
            command=self.ckbtn_create_folder_def
        )
        self.ckbtn_create_folder.pack(side=LEFT)
        self.ckbtn_down_video = Checkbutton(
            self.index2,
            text='下载视频',
            variable=self.ckbtn_down_video_var,
            command=self.ckbtn_down_videor_def
        )
        self.ckbtn_down_video.pack(side=LEFT)

        Button(
            self.index2, text='爬取单个作品',
            command=lambda: self.executor_ui.submit(self.get_work))\
            .pack(side=LEFT)
        Button(
            self.index2, text='爬取用户',
            command=lambda: self.executor_ui.submit(self.get_user_works))\
            .pack(side=LEFT)
        Button(
            self.index2, text='打开最新保存文件夹',
            command=self.open_latest_folder)\
            .pack(side=LEFT, fill=X, expand=True)
        # 日志行
        Label(self.f_logs, text='Logs:').pack(side=LEFT)
        Label(self.f_logs, textvariable=self.perclip_text, anchor='e')\
            .pack(side=LEFT, fill=X, expand=True)
        # 第三行
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

    class RepeatingTimer(Timer):
        def run(self):
            while not self.finished.is_set():
                self.function(*self.args, **self.kwargs)
                self.finished.wait(self.interval)

    def set_perclip_text(self):
        self.perclip_text.set('剪切板：{}'.format(pyperclip.paste()[0:75]))

    def __init__(self, version):
        self.core = Core(self.app_log)  # 可以让core库里调用本app.py的app_log()，不懂啥原理
        master = Tk()
        Frame.__init__(self, master)    # 这个能解决报错，但为什么，不懂。
        master.title("ArtStation Image Downloader " + version)
        # master.iconbitmap(r'.\icon\icon.ico')
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
        t = self.RepeatingTimer(1, self.set_perclip_text)
        t.start()


if __name__ == '__main__':
    # 显示GUI
    app = App(version=' GUI Test')
    app.mainloop()
    app.quit()
    exit()
