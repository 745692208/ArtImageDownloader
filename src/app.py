import os
from concurrent import futures

from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
'''
from tkinter import Tk, Frame, Label, Button, Scrollbar, Text, Entry, messagebox, filedialog  # 引入Tkinter工具包
from tkinter import TOP, LEFT, BOTTOM, BOTH, X, Y, END
from tkinter import ttk
'''
import config
from core import Core

class App(Frame):
    def app_log(self, value):
        print('log')
        self.logs_box.configure(state="normal")
        self.logs_box.insert(END, value + '\n')
        self.logs_box.see(END)
        self.logs_box.configure(state="disabled")

    def browse(self):
        print('browse')
        dir = os.path.normpath(tkinter.filedialog.askdirectory())
        if dir:
            config.write_config('config.ini', 'Paths', 'root_path', dir)
            self.save_path = dir
            self.entry_path.delete(0, END)
            self.entry_path.insert(0, self.save_path)

    def run(self):
        print('run')
        #self.btn.configure(state="disabled")
        self.core.b_is_create_folder = self.ckbtn_create_folder_var.get()
        self.core.file_save_dir = self.entry_path.get()
        self.core.run()
        #self.btn.configure(state="normal")

    def open_folder(self):
        try:
            os.startfile(self.entry_path.get())
        except:
            message = tkinter.messagebox.showerror("错误", "请输入正确的文件夹路径")

    def test(self):
        print(self.ckbtn_create_folder_var.get())

    def createWidgets(self):
        ''' ======== GUI设置 ======== '''
        
        #self.ckbtn_create_folder_var = BooleanVar()
        self.ckbtn_create_folder_var = IntVar()

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
        #self.entry_path.insert(0, 'E:\Python\down')
        
        Button(self.index1, text='浏览', command = self.browse).pack(side=LEFT)
        Button(self.index1, text='打开文件夹', command=self.open_folder).pack(side=LEFT)
        btn_run = Button(self.index1, text='剪切板爬取', command=lambda: self.executor_ui.submit(self.run))
        btn_run.pack(side=LEFT)
        self.ckbtn_create_folder = Checkbutton(self.index1, text='创建文件夹', variable=self.ckbtn_create_folder_var,  command=self.test)
        self.ckbtn_create_folder.pack(side=LEFT)
        Checkbutton(self.index1, text='Is 2D?').pack(side=LEFT)
        Label(self.index2, text='Logs:').pack(side=LEFT)

        self.logs_box = Text(self.index3)
        self.logs_box.pack(side=LEFT, fill=BOTH, expand=True)
        self.logs_box.configure(state="disabled")
        self.logs_box.focus()

        self.scrollbar = Scrollbar(self.index3)
        self.scrollbar.pack(side=LEFT, fill=Y)
        self.scrollbar.config(command=self.logs_box.yview)
        self.logs_box.config(yscrollcommand=self.scrollbar.set)

        self.lbl_status = Label(self.root, text='By:levosaber')
        self.lbl_status.pack(side=LEFT, fill=X, expand=True)
    
    def __init__(self, version):
        self.core = Core(self.app_log)  #可以让core库里调用本app.py的app_log()，不懂啥原理
        master = Tk()
        Frame.__init__(self, master)    #这个能解决报错，但为什么，不懂。
        master.title("ArtStation Image Downloader " + version)
        self.core = Core()
        self.root = master
        self.save_path = config.read_config('config.ini', 'Paths', 'root_path')
        self.executor_ui = futures.ThreadPoolExecutor(1)
        self.pack()
        self.createWidgets()
    
if __name__ == '__main__':
    #显示GUI
    app = App(version=' GUI Test')
    app.mainloop()