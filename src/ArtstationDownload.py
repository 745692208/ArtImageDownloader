import pyperclip  # pip install pyperclip
import requests  # pip install --upgrade urllib3==1.25.2
import json
import os
import webbrowser
import threading

import tkinter as tk
import tkinter.ttk as ttk


class App:

    def run_in_thread(fun):

        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=fun, args=args, kwargs=kwargs)
            thread.start()
            return thread

        return wrapper

    @run_in_thread
    def down_file(self, url, file_name, save_path):  # 下载图片
        '''下载输入的网址文件，并对其命名，保存到指定位置。
        :param url, str, 输入网页地址，如：https://cdna.artstation.com/p/1.jpg ;
        :param file_name, str, 文件保存名字，比如：awaw-5X9mYA-1.jpg ;
        :param save_path. str, 保存地址，比如：E:/asd '''
        session = requests.session()
        r = session.get(url)  # 下载图片
        path = os.path.join(save_path, file_name)  # 保存路径和文件名字合并
        with open(path, 'wb') as f:
            f.write(r.content)

    def make_name(self, j, index, url):
        username = j['user']['username']
        work_id = j['hash_id']
        ext = url.rsplit('.', 1)[1][0:3]  # jpg
        return f'{username}-{work_id}-{index}.{ext}'

    def download(self):
        save_path = self.savePath.get()
        p = pyperclip.paste()
        j = json.loads(p)

        for i, item in enumerate(j['assets']):
            print()
            if item['has_image']:
                url = item['image_url']
                name = self.make_name(j, i, url)
                print(name, url)
                self.down_file(url, name, save_path)

    def open_page(self):
        p = pyperclip.paste()
        work_id = p.rsplit('/', 1)[1]
        url = 'https://www.artstation.com/projects/{}.json'.format(work_id)
        webbrowser.open(url)

    def __init__(self, master=None):
        self.toplevel = tk.Tk() if master is None else tk.Toplevel(master)
        self.toplevel.title('ArtstationDownload v1.0')
        self.toplevel.geometry('500x100')
        self.savePath = tk.StringVar(value='D:/Test')
        # build ui
        self.f_main = ttk.Frame(self.toplevel)
        self.f1_savepath = ttk.Labelframe(self.f_main)
        self.entry_savepath = ttk.Entry(self.f1_savepath, textvariable=self.savePath)
        self.entry_savepath.pack(fill='x', side='top')
        self.f1_savepath.configure(height='200', text='Save Path', width='200')
        self.f1_savepath.pack(fill='x', side='top')
        self.button_open_page = ttk.Button(self.f_main, command=self.open_page)
        self.button_open_page.configure(text='Open Json Page by Clipboard')
        self.button_open_page.pack(fill='x', side='top')
        self.button_download = ttk.Button(self.f_main, command=self.download)
        self.button_download.configure(text='Download by Clipboard')
        self.button_download.pack(fill='x', side='top')
        self.f_main.configure(height='200', width='200')
        self.f_main.pack(fill='x', side='top')
        self.toplevel.configure(height='200', width='200')

        # Main widget
        self.mainwindow = self.toplevel

    def run(self):
        self.mainwindow.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
