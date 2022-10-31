import tkinter as tk
import tkinter.ttk as ttk
import os


class App:

    def __init__(self, master=None):
        # build ui
        ui_main = tk.Tk() if master is None else tk.Toplevel(master)

        # Options
        f = ttk.LabelFrame(ui_main, text='选项')
        f.pack(fill="x", side="top")
        # Options 1
        f2 = ttk.Frame(f)
        f2.pack(fill="x", side="top")

        a = ttk.Label(f2, justify="left", text='目录地址：')
        a.pack(side="left")

        self.dirpath = ttk.Entry(f2)
        self.dirpath.pack(expand="true", fill="x", side="left")
        ttk.Button(f2, text="浏览").pack(side="left")
        ttk.Button(f2, text="打开文件夹").pack(side="left")
        ttk.Separator(f2, orient="vertical").pack(fill="y", padx="5", pady="2", side="left")
        ttk.Button(f2, text="刷新").pack(side="left")
        # Options 2
        f2 = ttk.Frame(f)
        f2.pack(fill="x", side="top")
        self.a = ttk.Checkbutton(f2, text='自定义命名')
        self.a.pack(side="left")
        self.a = ttk.Checkbutton(f2, text='创建文件夹')
        self.a.pack(side="left")
        self.a = ttk.Checkbutton(f2, text='下载视频')
        self.a.pack(side="left")
        ttk.Button(f2, text="打开最近保存地址：xxx").pack(expand="true", fill="x", side="left")

        # Treeview
        self.selected_id = tk.StringVar()

        self.right_menu = tk.Menu(tearoff=False)
        self.right_menu.add_command(label='下载到此', command=self.save)
        self.right_menu.add_separator()
        self.right_menu.add_command(label='打开目录', command=self.open_folder)
        # self.right_menu.add_command(label='刷新', command=self.refresh)

        f = ttk.LabelFrame(ui_main, text='目录')
        f.pack(expand="true", fill="both", side="top")

        self.tv = ttk.Treeview(f, show='tree', displaycolumns=(), height=20)
        self.tv.pack(expand="true", fill="both", side="left")
        self.tv.bind('<Button-3>', self.right)  # 打开右键菜单

        sb = tk.Scrollbar(f)
        sb.pack(side="left", fill="y")
        sb['command'] = self.tv.yview
        self.tv.config(yscrollcommand=sb.set)  # 自动设置滚动条滑动幅度

        def list_all_dir(dirpath):
            name = os.path.split(dirpath)[1]

            # 筛选
            a = ['起稿', '2D', '2D图文教程', '3D', '3D图文教程', '现实参考', '素模']
            a = []
            if name in a:
                return

            all_path = [f'{dirpath}/{i}' for i in os.listdir(dirpath)]
            folders = [i for i in all_path if os.path.isdir(i)]
            files = [i for i in all_path if os.path.isdir(i) is False]

            r = {
                'name': name,
                'path': dirpath,
                'folders': [list_all_dir(i) for i in folders],
                'files': files,
            }
            return r

        def create_item(date={}, p=''):
            if date is None:
                return
            # 指定插入位置，0表示在头部插入，end表示在尾部插入。
            p = self.tv.insert(p, 'end', text=date['name'], values=date['path'])
            self.tv.item(p, open=False)  # 设置展开
            for d in date['folders']:
                create_item(d, p)
            return

        path = 'E:/Art/Resources/图库/CG图片'
        if os.path.exists(path):
            for d in list_all_dir(path)['folders']:
                create_item(d)

        # 日志
        f = ttk.LabelFrame(ui_main, text='日志')
        f.pack(fill="both", side="top")

        # 剪切板提醒
        a = ttk.Label(f, justify="left", textvariable='asd')  # textvariable=self.perclipText
        a.pack(expand="false", fill="x", side="top")

        f2 = ttk.Frame(f)
        f2.pack(fill="x", side="top")

        sb = ttk.Scrollbar(f2)
        sb.pack(side='right', fill='y')
        self.ui_logs_text = tk.Text(f2, yscrollcommand=sb.set)
        self.ui_logs_text.pack(expand="true", fill="both", side="left")
        self.ui_logs_text.configure(height=10, state="disabled")
        sb.config(command=self.ui_logs_text.yview)

        # Main widget
        self.mainwindow = ui_main

    def run(self):
        self.mainwindow.mainloop()

    def right(self, event):
        id = self.tv.identify_row(event.y)
        if id:
            self.selected_id.set(id)
            self.tv.selection_set(id)  # 设置tv当前选择项
            self.right_menu.post(event.x_root, event.y_root)

    def open_folder(self):
        path = self.tv.item(self.selected_id.get())['values'][0]
        os.startfile(path)

    def save(self):
        pass

    def refresh(self):
        pass


if __name__ == "__main__":
    app = App()
    app.run()
