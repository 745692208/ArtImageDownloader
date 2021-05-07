'''
import re
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
from concurrent import futures
from multiprocessing import cpu_count
from urllib.parse import urlparse  # pip install parse.urljoin
import pyperclip
import pafy
'''
import os
import re
import requests   # pip install --upgrade urllib3==1.25.2

# 全局变量
save_path = r'E:\Python\down\test'
session = requests.session()
b_is_create_folder = True


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
    # 1 获取json数据网址
    url = 'https://www.artstation.com/projects/{}.json'.format(
        url.rsplit('/', 1)[1])
    print(url)
    # 2 获取json资产数据
    session = requests.session()
    r = session.get(url)
    j = r.json()
    assets = j['assets']    # 获取资产
    if b_is_create_folder:
        title = j['slug'].strip()   # 获取标题
        print(title)
    # 3 资产数据分析
    for i, asset in enumerate(assets):
        print(i)
        if asset['asset_type'] == 'image':
            print('图片', asset['image_url'])
            url = asset['image_url']
            file_name = get_file_name(asset['image_url'], i, 1)
            down_file(url, file_name)  # 下载
        if asset['asset_type'] == 'video':
            print('Youtube视频')
            url = re.findall(r'src="(.*?)"', asset['player_embedded'])[0]
            print(url)
        if asset['asset_type'] == 'video_clip':
            print('A站视频')
            url = re.findall(r"src='(.*?)'", asset['player_embedded'])[0]
            print(url)
            r = session.get(url)
            # 获取可下载的网页地址
            source_media = re.findall(r'src="(.*?)" type=', r.text)[0]
            file_name = get_file_name(source_media, i, 0)
            print(source_media)
            down_file(source_media, file_name)  # 下载
    return j


def get_file_name(url, index, has_mask):
    '''
    把输入的网页地址转换成名字。
    :param url, str, 输入网页地址，
    如：https://cdna.artstation.com/..../gabriel-dias-maia-principal.jpg?1620144337；
    :param index, int, 尾缀index号；
    :param has_mask, bool, 网页地址的最后是否有问号，如上面的那个地址所示，去掉问号及其后面的东西；
    '''
    file_name = url.split('/')[-1]
    if has_mask:
        file_name = file_name.rsplit('?')[0]
    file_name = file_name.rsplit('.', 1)    # 分割名字和格式 name&jpg
    file_name = '{}-{}.{}'.format(file_name[0], index, file_name[1])
    return file_name


def down_file(url, file_name):   # 下载图片
    print('down_file', url, file_name)
    r = session.get(url)  # 下载图片
    path = os.path.join(save_path, file_name)   # 保存路径和文件名字合并
    print(path)
    with open(path, 'wb') as f:
        f.write(r.content)
    print('完成{}下载'.format(file_name))


def down_youtube_video(url, file_name):   # 下载视频
    print('down_youtube_video')


print('Run')
a = get_work('https://www.artstation.com/artwork/5X9mYA')
