#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import os
import time
from threading import Timer


def list_all_dir(dirpath):
    name = os.path.split(dirpath)[1]

    # 筛选
    a = ['起稿', '2D', '2D图文教程', '3D', '3D图文教程', '现实参考']
    if name in a:
        return

    all_path = [os.path.join(dirpath, i) for i in os.listdir(dirpath)]
    folders = [i for i in all_path if os.path.isdir(i)]
    files = [i for i in all_path if os.path.isdir(i) is False]

    r = {
        'name': name,
        'path': dirpath,
        'folders': [list_all_dir(os.path.join(dirpath, i)) for i in folders],
        'files': files,
    }
    return r


def create_item(f, date={}, i=0):
    if date is None:
        return
    a = EventCmd(date['path'])

    f2 = ttk.Frame(f)
    f2.pack(fill="x", side="top", padx=i * 20)

    # fold = ttk.Button(f2, style="Toolbutton", text='↓')
    v = tk.IntVar(value=0)
    fold = ttk.Checkbutton(f2, variable=v)
    fold.pack(side="left")
    if v.get():
        w = ttk.Button(f2, style="Toolbutton", text=date['name'])
        w.pack(expand="true", fill="x", side="left")
        w.bind("<Button-1>", a.left_click)
        w.bind("<Button-3>", a.right_click)
        for d in date['folders']:
            create_item(f, d, i + 1)


class EventCmd():

    def __init__(self, path):
        self.path = path

    def left_click(self, event):
        print(f'Run: {self.path}')

    def right_click(self, event):
        os.startfile(self.path)


class App:

    def __init__(self, master=None):
        # build ui
        toplevel1 = tk.Tk() if master is None else tk.Toplevel(master)
        f = ttk.Frame(toplevel1)
        f.pack(expand="true", fill="both", side="top")

        path = 'E:/Art/Resources/图库/CG图片'
        for d in list_all_dir(path)['folders']:
            create_item(f, d, 0)

        # Main widget
        self.mainwindow = toplevel1

    def run(self):

        def asd():
            while True:
                time.sleep(1)
                print('??')
                self.mainwindow.update()
                # self.mainwindow.

        t = Timer(1, asd)
        t.start()
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
