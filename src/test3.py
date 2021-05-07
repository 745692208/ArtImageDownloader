from concurrent import futures
from multiprocessing import cpu_count
import time
from tkinter import *

class core():
    def __init__(self):
        max_workers = cpu_count()*4
        self.executor = futures.ThreadPoolExecutor(max_workers*4)
        self.futures_list = []

    def asd(self, i):
        time.sleep(1)
        print(i)

    def qwe(self):
        
        for i in range(5):
            self.futures_list.append(self.executor.submit(self.asd, i))  # 异步加载，避免GUI卡顿
        futures.wait(self.futures_list)
        #aaa = self.futures_list.append(self.executor.submit(self.asd, i))  # 异步加载，避免GUI卡顿

        #aaa = self.executor.submit(self.asd, 5)  # 异步加载，避免GUI卡顿
        #futures.wait(aaa)
        print('down')

root=Tk()
root.geometry('340x150')
executor_ui = futures.ThreadPoolExecutor(1)
def but():
    a=core()
    a.qwe()

Button(root, text='button', command=lambda: executor_ui.submit(but)).pack()

root.mainloop()