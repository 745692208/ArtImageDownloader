import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
import os
import re
import sys
import time
import configparser
import webbrowser as web
from threading import Timer, Thread
from concurrent import futures
import pyperclip  # pip install pyperclip
import requests  # pip install --upgrade urllib3==1.25.2

# import json
# from multiprocessing import cpu_count

# =============================== 全局变量 ===============================
ui_name = "Art Image Downloader"
ui_version = "1.3.9.231205 by levosaber"


# =============================== 计时器 ===============================
class RepeatingTimer(Timer):
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


# =============================== Config ===============================
class Config:
    def load(self, field, key, *failValue):
        """读取
        :param *failValue, None, 读取失败后，返回的值。默认返回'';"""
        if len(failValue) == 0:
            failValue = ""
        else:
            failValue = failValue[0]
        cf = configparser.ConfigParser()
        try:
            cf.read(self.path, encoding="utf-8")
            if field in cf:
                result = cf.get(field, key)
            else:
                return failValue
        except Exception:
            return failValue
        return result

    def save(self, field, key, value):
        """保存"""
        cf = configparser.ConfigParser()
        try:
            cf.read(self.path, encoding="utf-8")
            if field not in cf:
                cf.add_section(field)
            cf.set(field, key, value)
            cf.write(open(self.path, "w", encoding="utf-8"))
        except Exception:
            return False
        return True

    def __init__(self, name):
        """Config使用整合，通过设置ini文件路径，使用save、load方法，即可便捷使用。
        :param name, str, 默认文件夹和ini的名字。"""
        self.cf = configparser.ConfigParser()
        self.path = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.path = self.path + "/" + name + ".ini"
        print(self.path)


# =============================== Core ===============================
class Core:
    def __init__(self, app_print=None, cf=None):
        self.app_print = app_print
        self.cf = cf
        # self.executor = futures.ThreadPoolExecutor(cpu_count() * 4)
        self.executor = futures.ThreadPoolExecutor()
        self.executor_video = futures.ThreadPoolExecutor()
        self.session = requests.session()
        self.isCustomName = True
        self.isCreateFolder = True
        self.isDownloadVideo = False
        self.useAutoDownload = False
        self.savePath = ""
        self.lastSavePath = ""

    # 工具 ------------------
    def print_log(self, str):
        if self.app_print:
            self.app_print(str)
        else:
            print(str)

    def session_get(self, url):
        # 解决403: https://blog.csdn.net/yuan2019035055/article/details/127597650
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"}
        try:
            r = self.session.get(url, headers=headers)
            self.print_log("网络连接成功，正在分析数据，请稍等...")
            if r.status_code == 200:
                return r
            elif r.status_code == 403:
                self.print_log("网络连接失败, 错误: 403;")
                return False
        except Exception as e:
            self.print_log(f"Error: {e};")
            return False

    def down_file(self, url, file_name, save_path):  # 下载图片
        """下载输入的网址文件，并对其命名，保存到指定位置。
        :param url, str, 输入网页地址，如：https://cdna.artstation.com/p/1.jpg ;
        :param file_name, str, 文件保存名字，比如：awaw-5X9mYA-1.jpg ;
        :param save_path. str, 保存地址，比如：E:/asd"""
        r = self.session.get(url)  # 下载图片
        path = os.path.join(save_path, file_name)  # 保存路径和文件名字合并
        with open(path, "wb") as f:
            f.write(r.content)

    def make_name(slef, name, index, format):
        """通过输入的参数，合成名字，name1-name2-index.format
        :param index, int, 请输入0开始的，因为会自动+1"""
        return f"{name}-{index + 1}.{format}"

    def make_save_path(slef, name):
        """输入名字并判断是否需要创建文件夹，最终制作保存路径"""
        if slef.isCreateFolder:
            return os.path.join(slef.savePath, name)
        return slef.savePath

    def check_make_dir(self, path):
        """检查输入的路径是否有效，无效则尝试创建文件夹，最终成功后保存路径"""
        self.lastSavePath = path
        self.cf.save("a", "lastSavePath", path)
        if os.path.exists(path):
            return True
        else:
            try:
                os.makedirs(path, exist_ok=True)
                self.print_log(f"保存地址：{path}")
                return True
            except Exception as e:
                messagebox.showerror("错误", "请输入正确的文件夹路径！")
                self.print_log(e)
                return False

    # A站 ------------------
    def get_user_works(self, url):  # 获取用户的所有作品
        """
        :param url, str, 网页地址，比如：https://www.artstation.com/pouria_roshan
        """
        self.print_log("分析中，请不要进行操作...")
        username = url.split("/")[-1]
        data = []
        page = 0  # 一页最大data数为50，0~49，page为1起步
        while True:
            page += 1
            url = f"https://www.artstation.com/users/{username}/projects.json?page={page}"
            j = self.session_get(url)
            if j is False:
                break
            j = j.json()
            total_count = int(j["total_count"])
            data += j["data"]
            if page > total_count / 50:
                break
        self.print_log(f"作者：{username}，共计{len(data)}个作品，现进行作品分析... ")
        futures_list = []
        for wrok in data:
            futures_list.append(self.executor.submit(self.get_work, wrok["permalink"]))
        futures.wait(futures_list)
        self.print_log("爬取用户作品的下载任务已全部完成；\n")

    def get_work(self, url):
        """
        获取单独作品
        :param url, str, 网页地址，比如：https://www.artstation.com/artwork/5X9mYA ;"""
        # 获取json资产数据
        self.print_log(f"分析网址：{url}，请稍等...")
        work_id = url.rsplit("/", 1)[1]
        url = f"https://www.artstation.com/projects/{work_id}.json"
        j = self.session_get(url)
        if j is False:
            return
        j = j.json()
        assets = j["assets"]  # 获取资产
        for i, asset in enumerate(assets):  # 删除多余资产
            if asset["asset_type"] == "cover":
                del assets[i]
        # 创建文件夹
        title = j["title"].strip()  # 获取标题
        title = re.sub(r'[/\:*?"<>|]', "", title)  # 去除标题特殊符号
        work_name = self.custom_name(j, work_id)  # pouria_roshan-5X9mYA
        path = self.make_save_path(title)  # D:\python\down\Buttercup
        self.check_make_dir(path)
        # 3 资产数据分析
        self.print_log(f"分析完毕, 作品: {title}，现进行下载...")
        futures_list = []
        for i, asset in enumerate(assets):
            if asset["asset_type"] == "image":
                url = asset["image_url"].rsplit("?", 1)[0]
                file_format = url.rsplit(".", 1)[1]  # .jpg
                name = self.make_name(work_name, i, file_format)
                self.print_log(f"图片：{url}")
                futures_list.append(self.executor.submit(self.down_file, url, name, path))
            elif asset["asset_type"] == "video_clip" and self.isDownloadVideo:
                url = re.findall(r"src='(.*?)'", asset["player_embedded"])[0]
                r = self.session_get(url)
                if r is False:
                    break
                source_media = re.findall(r'src="(.*?)" type=', r.text)[0]
                file_format = source_media.rsplit(".", 1)[1]  # .jpg
                name = self.make_name(work_name, i, file_format)
                self.print_log(f"视频：{source_media}")
                futures_list.append(self.executor.submit(self.down_file, source_media, name, path))
        futures.wait(futures_list)
        self.print_log(f"下载任务已完成：{work_id}\n")

    def custom_name(self, j, file_name):
        if self.isCustomName:
            username = j["user"]["username"]
            work_id = j["hash_id"]
            file_name = file_name.rsplit(".", 1)
            return f"{username}-{work_id}"
        else:
            return file_name

    # zb ------------------
    def zb_get_work(self, url):
        self.print_log(f"分析网址：{url}，请稍等...")
        r = self.session_get(url)
        if r is False:
            return
        r = r.text
        # 图片
        urls = re.findall(r"jpeg 1.5x, //(.*?) 2x", r)
        work_name = f'{url.rsplit("/", 2)[1]}-{url.rsplit("/", 2)[2]}'  # SwordGirl-402912
        path = self.make_save_path(work_name)
        self.check_make_dir(path)
        futures_list = []
        for i, url in enumerate(urls):
            url = "https://" + url
            name = self.make_name(work_name, i, "jpeg")
            self.print_log(f"图片：{url}")
            futures_list.append(self.executor.submit(self.down_file, url, name, path))
        # 视频
        if self.isDownloadVideo:
            urls_video = re.findall(r"www(.*?)mp4", r)
            work_name = work_name + "_video"
            for i, video_url in enumerate(urls_video):
                video_url = "https://www" + video_url + "mp4"
                name = self.make_name(work_name, i, "mp4")
                self.print_log(f"视频：{video_url}")
                futures_list.append(self.executor.submit(self.down_file, video_url, name, path))
        futures.wait(futures_list)
        self.print_log(f"下载任务已完成：{work_name}\n")


# =============================== App ===============================
class App:
    # 子线程
    def run_in_thread(fun):
        def wrapper(*args, **kwargs):
            thread = Thread(target=fun, args=args, kwargs=kwargs)
            thread.daemon = True  # 设置线程为守护线程，防止退出主线程时，子线程仍在运行
            thread.start()
            return thread

        return wrapper

    def set_perclipText(self):
        p = pyperclip.paste()[0:75]
        text = f"剪切板：{p}"
        if self.useAutoDownload.get() == 1:
            if text not in self.perclipText.get():
                try:
                    self.on_down_current()
                except Exception as e:
                    print(e)
        # 设置最近保存路径提示
        self.perclipText.set(text.replace("\n", "").replace("\r", ""))
        text = "打开最近保存：" + self.c.lastSavePath
        self.lastSaveText.set(text)

    def on_OpenConfig(self):
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        path = path + "/" + ui_name + ".ini"
        try:
            os.startfile(path)
            self.app_log(path)
        except Exception:
            self.app_log("没有ini文件，请先保存ini。")

    def SaveConfig(self):
        self.cf.save("a", "savePath", self.savePath.get())
        self.cf.save("a", "isCustomName", str(self.isCustomName.get()))
        self.cf.save("a", "isCreateFolder", str(self.isCreateFolder.get()))
        self.cf.save("a", "isDownloadVideo", str(self.isDownloadVideo.get()))
        self.cf.save("a", "useAutoDownload", str(self.useAutoDownload.get()))
        self.cf.save("a", "exclude", self.exclude.get())
        self.update_all_open()
        self.cf.save("a", "all_open", str(self.all_open))

    def loadConfig(self):
        self.savePath.set(self.cf.load("a", "savePath", "D:/Test"))
        self.isCustomName.set(int(self.cf.load("a", "isCustomName", "1")))
        self.isCreateFolder.set(int(self.cf.load("a", "isCreateFolder", "0")))
        self.isDownloadVideo.set(int(self.cf.load("a", "isDownloadVideo", "1")))
        self.useAutoDownload.set(int(self.cf.load("a", "useAutoDownload", "1")))
        self.c.lastSavePath = self.cf.load("a", "lastSavePath", "D:/Test")
        self.exclude.set(self.cf.load("a", "exclude", "素模"))
        self.all_open = eval(self.cf.load("a", "all_open", "{}"))

    def on_OpenLastFolder(self):
        os.startfile(self.c.lastSavePath)
        self.app_log(f"打开最近保存文件夹：{self.c.lastSavePath}")

    def on_OpenFolder(self, name=""):
        path = os.path.join(self.savePath.get(), name)
        os.startfile(path)
        self.app_log(f"打开文件夹：{path}")

    def on_Browse(self):
        dir = os.path.normpath(filedialog.askdirectory())
        if dir != ".":
            self.savePath.set(dir)
            self.SaveConfig()

    def on_down_current(self):
        id = self.tv.selection()[0]
        if id:
            self.selected_id.set(id)
            self.tv.selection_set(id)  # 设置tv当前选择项
        self.on_Download()

    def on_if_existing(self):
        def get_exist_path(folder={}, k=""):
            """:param d dict:{"name": "", "path": "", "folders": [], "files": []}"""
            if k in str(folder.get("files")):
                return folder["path"]
                # r = folder["path"]
            else:
                for f in folder["folders"]:
                    r = get_exist_path(f, k)
                    if r is not None:
                        return r
            return None

        code = pyperclip.paste()[-6:]
        path = self.savePath.get()
        exist_path = get_exist_path(self.list_all_dir(path), code)
        if exist_path:
            self.app_log(f" {code} 已存在, 路径: {exist_path}")
        else:
            self.app_log(f" {code} 不存在!")

    def app_log(self, value):
        time_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        value = f"[{time_date}]{value}"
        self.ui_logs_text.configure(state="normal")
        self.ui_logs_text.insert("end", value + "\n")
        self.ui_logs_text.see("end")
        self.ui_logs_text.configure(state="disabled")

    @run_in_thread
    def on_Download(self):
        self.SaveConfig()
        url = pyperclip.paste()
        self.c.isCustomName = self.isCustomName.get()
        self.c.isCreateFolder = self.isCreateFolder.get()
        self.c.isDownloadVideo = self.isDownloadVideo.get()
        path = self.tv.item(self.selected_id.get())["values"][0]
        self.c.savePath = path
        if "zbrushcentral" in url:
            self.c.zb_get_work(url)
        elif "artstation" in url:
            if "artwork" in url:  # 判断是否为单个作品，否则为用户
                self.c.get_work(url)
            else:
                self.c.get_user_works(url)
        else:
            self.app_log("剪切板中信息有误，无法爬取数据。")

    def create_ui(self, master=None):
        # build ui
        ui_main = tk.Tk() if master is None else tk.Toplevel(master)
        ui_main.title(f"{ui_name} {ui_version}")
        # build variable
        self.savePath = tk.StringVar(value="D:/Test")
        self.isCustomName = tk.IntVar(value=1)
        self.useAutoDownload = tk.IntVar(value=0)
        self.isDownloadVideo = tk.IntVar(value=1)
        self.isCreateFolder = tk.IntVar(value=1)
        self.lastSavePath = ""
        self.perclipText = tk.StringVar(value="")
        self.lastSaveText = tk.StringVar(value="打开最近保存文件夹")
        self.exclude = tk.StringVar(value="")
        self.all_open = {}
        self.loadConfig()
        # 00 menu -----------------------------------
        menubar = tk.Menu(ui_main)
        options = tk.Menu(menubar, tearoff=0)
        options.add_command(label="Open.ini", command=self.on_OpenConfig)
        options.add_command(label="Save.ini", command=self.SaveConfig)
        menubar.add_cascade(label="Options", menu=options)
        # about
        about = tk.Menu(menubar, tearoff=0)
        a = "https://github.com/745692208/ArtImageDownloader"
        about.add_command(label="Github", command=lambda: web.open(a))
        about.add_separator()
        a = "https://www.artstation.com/"
        about.add_command(label="ArtStion", command=lambda: web.open(a))
        a = "https://www.zbrushcentral.com/"
        about.add_command(label="ZBrushcentral", command=lambda: web.open("https://www.zbrushcentral.com/"))
        menubar.add_cascade(label="About", menu=about)
        ui_main["menu"] = menubar
        # 01 options -----------------------------------
        ui_f1 = ttk.Frame(ui_main)
        ui_f1.pack(fill="x", side="top")
        a = ttk.Label(ui_f1, justify="left", text="Save Path：")
        a.pack(side="left")
        a = ttk.Entry(ui_f1, textvariable=self.savePath)
        a.pack(expand="true", fill="x", side="left")
        a = ttk.Button(ui_f1, text="浏览", command=self.on_Browse)
        a.pack(side="left")
        # btn 打开文件夹-----
        a = ttk.Button(ui_f1, text="打开文件夹", command=self.on_OpenFolder)
        a.pack(side="left")
        # btn 刷新-----
        a = ttk.Separator(ui_f1, orient="vertical")
        a.pack(fill="y", padx="5", pady="2", side="left")
        a = ttk.Button(ui_f1, text="刷新", command=self.refresh)
        a.pack(side="left")
        # 02 options -----------------------------------
        f = ttk.Frame(ui_main)
        f.pack(fill="x", side="top")
        a = ttk.Label(f, justify="left", text="排除关键字(','分割)：")
        a.pack(side="left")
        a = ttk.Entry(f, textvariable=self.exclude)
        a.pack(expand="true", fill="x", side="left")
        # 03 options -----------------------------------
        ui_f2 = ttk.Frame(ui_main)
        ui_f2.pack(fill="x", side="top")
        # cb 自定义命名-----
        a = ttk.Checkbutton(ui_f2, text="自定义命名", variable=self.isCustomName)
        a.pack(side="left")
        # cb 创建文件夹-----
        a = ttk.Checkbutton(ui_f2, text="创建文件夹", variable=self.isCreateFolder)
        a.pack(side="left")
        # cb 下载视频-----
        a = ttk.Checkbutton(ui_f2, text="下载视频", variable=self.isDownloadVideo)
        a.pack(side="left")
        # btn 打开最近保存文件夹-----
        a = ttk.Button(ui_f2, textvariable=self.lastSaveText)
        a.configure(command=self.on_OpenLastFolder)
        a.pack(expand="true", fill="x", side="left")

        # Treeview
        self.selected_id = tk.StringVar()

        self.right_menu = tk.Menu(tearoff=False)
        self.right_menu.add_command(label="下载到此", command=self.on_Download)
        self.right_menu.add_separator()
        self.right_menu.add_command(label="打开目录", command=self.open_folder)

        f = ttk.LabelFrame(ui_main, text="目录")
        f.pack(expand="true", fill="both", side="top")

        self.tv = ttk.Treeview(f, show="tree", displaycolumns=(), height=20)
        self.tv.pack(expand="true", fill="both", side="left")
        self.tv.bind("<Button-3>", self.on_RightClick)  # 打开右键菜单

        sb = tk.Scrollbar(f)
        sb.pack(side="left", fill="y")
        sb["command"] = self.tv.yview
        self.tv.config(yscrollcommand=sb.set)  # 自动设置滚动条滑动幅度

        self.refresh()

        # 04 logs 日志 -----------------------------------
        f = ttk.LabelFrame(ui_main, text="日志")
        f.pack(fill="both", side="top")

        f2 = ttk.Frame(f)
        f2.pack(fill="x", side="top")

        # 剪切板提醒
        a = ttk.Label(f2, justify="left", textvariable=self.perclipText)
        a.pack(expand="true", fill="x", side="left")

        # 剪切板提醒 下
        f2 = ttk.Frame(f)
        f2.pack(fill="x", side="top")
        # 快速下载-----
        a = ttk.Checkbutton(f2, text="自动检测下载", variable=self.useAutoDownload)
        a.pack(side="left")
        # btn 下载-----
        a = ttk.Button(f2, text="下载到选择项")
        a.configure(command=self.on_down_current)
        a.pack(side="left")
        # btn 是否存在-----
        a = ttk.Button(f2, text="判断是否存在(A站)")
        a.configure(command=self.on_if_existing)
        a.pack(side="left")

        f2 = ttk.Frame(f)
        f2.pack(fill="x", side="top")

        sb = ttk.Scrollbar(f2)
        sb.pack(side="right", fill="y")
        self.ui_logs_text = tk.Text(f2, yscrollcommand=sb.set)
        self.ui_logs_text.pack(expand="true", fill="both", side="left")
        self.ui_logs_text.configure(height=10, state="disabled")
        sb.config(command=self.ui_logs_text.yview)

        # Main widget
        self.mainwindow = ui_main

    def on_RightClick(self, event):
        id = self.tv.identify_row(event.y)
        if id:
            self.selected_id.set(id)
            self.tv.selection_set(id)  # 设置tv当前选择项
            self.right_menu.post(event.x_root, event.y_root)

    def open_folder(self):
        path = self.tv.item(self.selected_id.get())["values"][0]
        os.startfile(path)

    def save(self):
        self.on_Download()
        pass

    def list_all_dir(self, dirpath):
        name = os.path.split(dirpath)[1]

        # 筛选
        if name in self.exclude_list:
            return None

        all_path = [f"{dirpath}/{i}" for i in os.listdir(dirpath)]
        folders = [i for i in all_path if os.path.isdir(i)]
        folders = [self.list_all_dir(i) for i in folders]
        files = [i for i in all_path if os.path.isdir(i) is False]

        r = {
            "name": name,
            "path": dirpath,
            "folders": [i for i in folders if i is not None],
            "files": files,
        }
        return r

    def update_all_open(self):
        def get_all_open(tv, p):
            a = {tv.item(p)["values"][0]: tv.item(p)["open"]}
            for i in tv.get_children(p):
                a.update(get_all_open(tv, i))
            return a

        a = {}
        for i in self.tv.get_children():
            a.update(get_all_open(self.tv, i))
        self.all_open = a

    def refresh(self):
        def create_item(date={}, p=""):
            if date is None:
                return
            # 指定插入位置，0表示在头部插入，end表示在尾部插入。
            v = date["path"].replace("\\", "/")
            p = self.tv.insert(p, "end", text=date["name"], values=[v])
            if self.all_open.get(v):
                self.tv.item(p, open=self.all_open[v])  # 设置展开
            for d in date["folders"]:
                create_item(d, p)
            return

        if len(self.tv.get_children()) > 0:
            self.update_all_open()

        # 清除现有的
        self.tv.delete(*self.tv.get_children())

        # 刷新
        path = self.savePath.get()
        self.exclude_list = self.exclude.get().split(",")
        if os.path.exists(path):
            for d in self.list_all_dir(path)["folders"]:
                create_item(d)
        self.SaveConfig()

    def __init__(self):
        self.session = requests.session()
        self.cf = Config(ui_name)
        self.c = Core(self.app_log, self.cf)
        self.create_ui()
        # 剪切板信息实时刷新
        self.t = RepeatingTimer(1, self.set_perclipText)
        self.t.name = "Thread-PerclipText"
        self.t.start()


if __name__ == "__main__":
    app = App()
    app.mainwindow.mainloop()
    app.t.cancel()
    time.sleep(1)
    sys.exit()
