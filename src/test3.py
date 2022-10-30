from tkinter import *
from tkinter import ttk  # 下拉菜单控件在ttk中
import tkinter.messagebox  # 弹出提示对话框
import tkinter.simpledialog  # 弹出对话框，获取用户输入
import os

top = Tk()  # 初始化Tk()
top.title('TEST')  # 设置标题
窗口宽 = 900
窗口高 = 600
# 获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
屏幕宽 = top.winfo_screenwidth()
屏幕高 = top.winfo_screenheight()
主窗口显示位置 = '%dx%d+%d+%d' % (窗口宽, 窗口高, (屏幕宽 - 窗口宽) / 2, (屏幕高 - 窗口高) / 2)
top.geometry(主窗口显示位置)
top.resizable(width=True, height=True)  # 设置窗口是否可变长、宽（True：可变，False：不可变）
top.grid_columnconfigure(1, weight=1)  # (第1列, 自适应窗口宽)

左框 = LabelFrame(top, text='左')
右框 = LabelFrame(top, text='右')
左框.grid(row=0, column=0, sticky='NSEW')
右框.grid(row=0, column=1, sticky='NSEW')

选中_TV_IID = StringVar()  # 保存变量，方便作为参数使用

根目录 = 'E:\\DATA_CACHE'


def 查目录(PATH_DIR):
    L = os.listdir(PATH_DIR)
    return (L)


def 读文件(PATH_FILE):
    f = open(PATH_FILE, 'r')
    S = f.read()
    f.close()
    return (S)


def TV在指定节点添加子项(父级IID, L_DATA):
    显示text, 类型, 本级值 = L_DATA
    本级IID = Treeview_结构.insert(父级IID, END, text=显示text, values=[类型, 父级IID, 本级值])
    print(f"  本级IID={本级IID}  父级IID={父级IID}  OBJ: {本级IID} = Treeview_结构.insert({父级IID}, END, text={显示text}, values={[类型, 父级IID, 本级值]})")


def DEF_打开根():
    PATH_DIR = 根目录
    顶级IID = Treeview_结构.insert('', END, text=PATH_DIR, values=['目录', '', PATH_DIR])  # 在根节点插入子节点（作为顶级顶点） # 指定插入位置，0表示在头部插入，END表示在尾部插入。
    print(f"顶级IID={顶级IID}  Treeview_结构.insert('', END, text={PATH_DIR}, values={['目录', '', PATH_DIR]})")
    Treeview_结构.item(顶级IID, open=True)  # 设置展开
    选中_TV_IID.set(顶级IID)
    DEF_打开目录()


def DEF_打开目录():
    选中IID = 选中_TV_IID.get()
    if 选中IID:
        Treeview_结构.selection_set(选中IID)
        选中名 = Treeview_结构.item(选中IID)["text"]
        类型, 父级IID, 本级值 = Treeview_结构.item(选中IID)['values']

        PATH_DIR = 本级值
        L = 查目录(PATH_DIR)
        if L == []:
            print(f"DEF_打开 PATH_DIR={PATH_DIR} 为 []")
        else:
            for i in L:
                PATH = os.path.join(本级值, i)
                if os.path.isdir(PATH):
                    L_DATA = [i, '目录', PATH]
                elif os.path.isfile(PATH):
                    L_DATA = [i, '文件', PATH]
                else:
                    L_DATA = [i, '未知', PATH]
                TV在指定节点添加子项(选中IID, L_DATA)
            DEF_TV_展开()


def DEF_打开文件():
    选中IID = 选中_TV_IID.get()
    if 选中IID:
        Treeview_结构.selection_set(选中IID)
        选中名 = Treeview_结构.item(选中IID)["text"]
        类型, 父级IID, 本级值 = Treeview_结构.item(选中IID)['values']
        PATH_FILE = f"{本级值}"
        内容 = 读文件(PATH_FILE)
        print(f"  DEF_打开文件 PATH_FILE={PATH_FILE} 选中IID={选中IID}({类型, 父级IID, 本级值}) 内容={内容}")


def DEF_TV_展开():
    选中IID = 选中_TV_IID.get()
    try:
        if Treeview_结构.item(选中IID)['open'] == 0:  # 判断未展开
            Treeview_结构.item(选中IID, open=True)  # 设置展开
            print(f"展开目录 {选中IID} 完成")
    except Exception as e:
        print(f"展开目录 {选中IID} 失败 {e}")


def DEF_TV_折叠():
    选中IID = 选中_TV_IID.get()
    try:
        if Treeview_结构.item(选中IID)['open'] != 0:  # 判断已展开
            Treeview_结构.item(选中IID, open=0)  # 设置折叠
            print(f"折叠目录 {选中IID} 完成")
    except Exception as e:
        print(f"折叠目录 {选中IID} 失败 {e}")


def DEF_右键菜单_刷新全部():
    items = Treeview_结构.get_children()
    [Treeview_结构.delete(item) for item in items]
    DEF_打开根()


def DEF_刷新子项():
    选中IID = 选中_TV_IID.get()
    items = Treeview_结构.get_children(选中IID)
    print(f"DEF_刷新子项 选中IID={选中IID} 子IID={items}")
    [Treeview_结构.delete(item) for item in items]
    DEF_打开目录()


def DEF_删除():
    选中IID = 选中_TV_IID.get()
    Treeview_结构.selection_set(选中IID)
    类型, 父级IID, 本级值 = Treeview_结构.item(选中IID)['values']
    PATH = 本级值
    if 类型 == '文件':
        try:
            os.unlink(PATH)
        except Exception as e:
            ERROR = f"删除 文件 {PATH} 失败 {e}"
            tkinter.messagebox.showerror(title='ERROR', message=ERROR)
        else:
            选中_TV_IID.set(父级IID)
            DEF_刷新子项()
    elif 类型 == '目录':
        try:
            os.rmdir(PATH)
        except Exception as e:
            ERROR = f"删除 目录 {PATH} 失败 {e}"
            tkinter.messagebox.showerror(title='ERROR', message=ERROR)
        else:
            选中_TV_IID.set(父级IID)
            DEF_刷新子项()


def DEF_新建文件():
    新建文件名 = tkinter.simpledialog.askstring(title='新建文件', prompt='新建文件名：')
    ## 确定为输入内容，取消为None
    if 新建文件名 != None:
        选中IID = 选中_TV_IID.get()
        Treeview_结构.selection_set(选中IID)
        类型, 父级IID, 本级值 = Treeview_结构.item(选中IID)['values']
        PATH = os.path.join(本级值, 新建文件名)
        try:
            f = open(PATH, 'w')
            f.write('测试新建文件')
            f.close()
        except Exception as e:
            ERROR = f"新建文件{PATH}失败{e}"
            tkinter.messagebox.showerror(title='ERROR', message=ERROR)
        else:
            DEF_刷新子项()


def DEF_新建目录():
    新建目录名 = tkinter.simpledialog.askstring(title='新建目录', prompt='新建目录名：')
    ## 确定为输入内容，取消为None
    if 新建目录名 != None:
        选中IID = 选中_TV_IID.get()
        Treeview_结构.selection_set(选中IID)
        类型, 父级IID, 本级值 = Treeview_结构.item(选中IID)['values']
        PATH = os.path.join(本级值, 新建目录名)
        try:
            os.makedirs(PATH)
        except Exception as e:
            ERROR = f"新建目录{PATH}失败{e}"
            tkinter.messagebox.showerror(title='ERROR', message=ERROR)
        else:
            DEF_刷新子项()


目录_右键菜单 = Menu(tearoff=False)
目录_右键菜单.add_command(label='打开目录', command=DEF_刷新子项)
目录_右键菜单.add_command(label='展开', command=DEF_TV_展开)
目录_右键菜单.add_command(label='折叠', command=DEF_TV_折叠)
目录_右键菜单.add_separator()
目录_右键菜单.add_command(label='新建文件', command=DEF_新建文件)
目录_右键菜单.add_command(label='新建目录', command=DEF_新建目录)
目录_右键菜单.add_command(label='刷新目录', command=DEF_刷新子项)
目录_右键菜单.add_separator()
目录_右键菜单.add_command(label='删除目录', command=DEF_删除)
目录_右键菜单.add_separator()
目录_右键菜单.add_command(label='刷新全部', command=DEF_右键菜单_刷新全部)

文件_右键菜单 = Menu(tearoff=False)
文件_右键菜单.add_command(label='打开文件', command=DEF_打开文件)
文件_右键菜单.add_command(label='删除文件', command=DEF_删除)

空白处_右键菜单 = Menu(tearoff=False)
空白处_右键菜单.add_command(label='空白处')


def DEF_鼠标右键(event):
    选中IID = Treeview_结构.identify_row(event.y)
    if 选中IID:
        选中_TV_IID.set(选中IID)
        Treeview_结构.selection_set(选中IID)  # 鼠标左键点击
        选中名 = Treeview_结构.item(选中IID)["text"]
        类型, 父级IID, 本级值 = Treeview_结构.item(选中IID)['values']
        print(f"DEF_鼠标右键 选中IID={选中IID} 选中名={选中名} 类型={类型} 父级IID={父级IID} 本级值={本级值}")
        if 类型 == '目录':
            目录_右键菜单.post(event.x_root, event.y_root)  # 光标位置显示菜单
        elif 类型 == '文件':
            文件_右键菜单.post(event.x_root, event.y_root)
    else:
        print("DEF_鼠标右键 【点在树外】")
        空白处_右键菜单.post(event.x_root, event.y_root)


Treeview_结构 = ttk.Treeview(左框, show='tree', displaycolumns=(), height=20)
#Treeview_结构.bind('<<TreeviewSelect>>', DEF_鼠标左键单击)
#Treeview_结构.bind('<Double-Button-1>', DEF_鼠标左键双击)
Treeview_结构.bind('<Button-3>', DEF_鼠标右键)  # 打开右键菜单
Scrollbar_竖 = Scrollbar(左框)
Scrollbar_竖['command'] = Treeview_结构.yview
Scrollbar_横 = Scrollbar(左框)
Scrollbar_横['command'] = Treeview_结构.xview
Scrollbar_横['orient'] = HORIZONTAL
Scrollbar_竖.grid(row=0, column=1, sticky=S + W + E + N)
Scrollbar_横.grid(row=1, column=0, sticky=S + W + E + N)
Treeview_结构.config(xscrollcommand=Scrollbar_横.set, yscrollcommand=Scrollbar_竖.set)  # 自动设置滚动条滑动幅度
Treeview_结构.grid(row=0, column=0, sticky='NSEW')


def DEF_ID查子项():
    选中IID = 选中_TV_IID.get()
    items = Treeview_结构.get_children(选中IID)
    print(f"选中IID={选中IID} 子IID={items}")


Button(右框, text='打开根目录', command=DEF_打开根).grid(row=0, column=0, sticky='NW')

Entry(右框, textvariable=选中_TV_IID).grid(row=1, column=0)
Button(右框, text='ID查子项', command=DEF_ID查子项).grid(row=1, column=1, sticky='NW')

top.mainloop()  ## 进入消息循环