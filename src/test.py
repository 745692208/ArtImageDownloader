#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
import os


def list_all_dir(dirpath):
    path, name = os.path.split(dirpath)

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
    a = EventCmd(date['path'])
    w = ttk.Button(f, style="Toolbutton", text=date['name'])
    w.pack(anchor="w", fill="x", side="top", padx=i * 20)
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
        self.mainwindow.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
