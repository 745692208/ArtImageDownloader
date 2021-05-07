from tkinter import *
import tkinter.messagebox
import re
import pyperclip
import GetImage

''' ======== GUI设置 ======== '''
top = Tk()
top.title("A站图片爬虫v1.0 By:levosaber")
top.geometry('400x200+100+100')

'''变量'''
tk_url = StringVar()
tk_url.set('')

'''事件'''
def tk_run():
    html = tk_url.get()
    urls = re.findall(r'image_url(.*?),', html)  # 正则表达式解析网页
    title = re.findall(r'<title>(.*?)</title>', html)[0]  # 正则表达式解析网页
    print(title)
    for i,url in enumerate(urls):
        urls[i] = urls[i].rsplit('"', 1)[0].rsplit('"', 1)[1]
        urls[i] = urls[i].rsplit('?', 1)[0]
        print(urls[i])
    GetImage.down_images(urls, title)

def tk_run_clip():
    tk_url.set(pyperclip.paste())
    tk_run()

def tk_hele():
    tkinter.messagebox.showinfo('使用说明','在A站作品页面中，按ctrl+u，打开页面源码，全选复制然后点击剪切板爬取按钮即可。')

'''控件'''
Label(text='Url：').grid(row=0, column=0)
Entry(textvariable = tk_url).grid(row=0, column=1)
Button(text='爬取', command=tk_run).grid(row=0, column=2)
Button(text='剪切板爬取', command=tk_run_clip).grid(row=0, column=3)

Label(text='指定保存目录').grid(row=1, column=0)
Entry().grid(row=1, column=1)

Label(text='VPN端口').grid(row=2, column=0)
Entry().grid(row=2, column=1)

Button(text='使用说明', command=tk_hele).grid(row=4, column=0, columnspan=4, sticky=EW)

'''显示GUI'''
top.mainloop()
