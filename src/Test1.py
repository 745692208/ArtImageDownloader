'''
import os
import re
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
from concurrent import futures
from multiprocessing import cpu_count
from urllib.parse import urlparse
import pyperclip
import pafy
'''
import requests

# 全局变量
save_path = r'D:\Python\down\test'


def get_user_works(url):  # 获取用户的所有作品
    '''
    :param url, str, 网页地址，比如：https://www.artstation.com/pouria_roshan
    '''
    print('get_user_works')


def get_work(url):  # 获取单独作品
    '''
    :param url, str, 网页地址，比如：https://www.artstation.com/artwork/5X9mYA
    '''
    print('get_work')
    # 1 网址编辑
    # url = 'https://www.artstation.com/artwork/5X9mYA'
    url = 'https://www.artstation.com/projects/{}.json'.format(
        url.rsplit('/', 1)[1])
    print(url)
    # 2 基本数据分析
    session = requests.session()
    r = session.get(url)
    j = r.json()
    assets = j['assets']    # 获取资产
    # title = j['slug'].strip()   #获取标题
    # 3 资产数据分析
    for i, asset in enumerate(assets):
        # print(asset)
        # print(' ')
        # print(type(asset['has_image']))
        print(i)
        if asset['has_image']:
            print('有图片', asset['image_url'])
        else:
            print('没有图片')

        if asset['has_embedded_player']:
            print('有视频', asset['player_embedded'])
        else:
            print('没有视频')

    return j


def down_image(url, file_name):   # 下载图片
    print('down_image')


def down_video(url, file_name):   # 下载视频
    print('down_video')


print('Run')
a = get_work('https://www.artstation.com/artwork/5X9mYA')
