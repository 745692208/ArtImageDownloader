import pyperclip  # pip install pyperclip
import requests  # pip install --upgrade urllib3==1.25.2
import json
import os
import webbrowser
import threading
import re
import time
import sys

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
        ext = url.rsplit('.', 1)[1]  # jpg
        if '?' in ext:
            ext = ext.rsplit('?', 1)[0]
        return f'{username}-{work_id}-{index}.{ext}'

    def download(self):
        save_path = self.savePath.get()
        if os.path.exists(save_path) is False:
            os.makedirs(save_path)
        j = json.loads(pyperclip.paste())
        for i, item in enumerate(j['assets']):
            if item['asset_type'] == 'image':
                url = item['image_url']
            elif item['asset_type'] == 'video_clip':
                url = re.findall(r"src='(.*?)'", item['player_embedded'])[0]
                r = self.session.get(url)
                url = re.findall(r'src="(.*?)" type=', r.text)[0]
            # 下载
            name = self.make_name(j, i, url)
            self.down_file(url, name, save_path)
            print(name, url)

    def open_page(self):
        p = pyperclip.paste()
        work_id = p.rsplit('/', 1)[1]
        url = 'https://www.artstation.com/projects/{}.json'.format(work_id)
        webbrowser.open(url)

    def __init__(self):
        self.session = requests.session()
        # TK
        toplevel = tk.Tk()
        toplevel.title('ArtstationDownload v1.0')
        toplevel.geometry('500x100')
        # Var
        self.savePath = tk.StringVar(value='D:/Test')
        # UI
        f0 = ttk.Frame(toplevel)
        f0.pack(fill='x', side='top')
        f1 = ttk.Labelframe(f0, text='Save Path')
        f1.pack(fill='x', side='top')
        ttk.Entry(f1, textvariable=self.savePath).pack(fill='x', side='top')
        ttk.Button(f0, text='Open Json Page by Clipboard', command=self.open_page).pack(fill='x', side='top')
        ttk.Button(f0, text='Download by Clipboard', command=self.download).pack(fill='x', side='top')
        # main window
        self.mainwindow = toplevel

    def run(self):
        self.mainwindow.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
    time.sleep(1)
    sys.exit()
