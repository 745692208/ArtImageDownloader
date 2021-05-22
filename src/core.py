import os
import re
import sys
from concurrent import futures
from multiprocessing import cpu_count
from tkinter import messagebox

import you_get  # pip install you_get
import requests   # pip install --upgrade urllib3==1.25.2
from pytube import YouTube  # https://pytube.io/en/latest/user/install.html
import config


class ArtStation:
    def __init__(self):
        self.b_is_down_video = True

    def get_user_works(self, url):  # 获取用户的所有作品
        '''
        :param url, str, 网页地址，比如：https://www.artstation.com/pouria_roshan
        '''
        print('分析中，请不要进行操作...')
        username = url.split('/')[-1]
        data = []
        page = 0    # 一页最大data数为50，0~49，page为1起步
        while True:
            page += 1
            url = 'https://www.artstation.com/users/{}/projects.json?page={}'\
                .format(username, page)
            j = u.session_get(url).json()
            total_count = int(j['total_count'])
            data += j['data']
            if page > total_count / 50:
                break
        print('分析完毕，作者：{}，共计{}个作品，现进行作品分析... '.format(username, len(data)))
        futures_list = []
        for wrok in data:
            futures_list.append(
                executor.submit(self.get_work, wrok['permalink']))
        futures.wait(futures_list)
        print("[正常]爬取用户作品的下载任务已全部完成；\n")

    def get_work(self, url):
        '''
        获取单独作品
        :param url, str, 网页地址，比如：https://www.artstation.com/artwork/5X9mYA ;'''
        # 获取json资产数据
        print('分析网址：{}中，请不要进行操作...'.format(url))
        work_id = url.rsplit('/', 1)[1]
        url = 'https://www.artstation.com/projects/{}.json'.format(work_id)
        j = u.session_get(url).json()
        assets = j['assets']    # 获取资产
        for i, asset in enumerate(assets):    # 删除多余资产
            if asset['asset_type'] == 'cover':
                del assets[i]
        # 创建文件夹
        title = j['title'].strip()   # 获取标题
        title = re.sub(r'[/\:*?"<>|]', "", title)    # 去除标题特殊符号
        work_name = self.custom_name(j, work_id)  # pouria_roshan-5X9mYA
        path = u.make_save_path(title)  # D:\python\down\Buttercup
        u.check_make_dir(path)
        # 3 资产数据分析
        print('分析完毕，作品：{}，现进行下载...'.format(j['title'].strip()))
        futures_list = []
        for i, asset in enumerate(assets):
            if asset['asset_type'] == 'image':
                url = asset['image_url'].rsplit('?', 1)[0]
                file_format = url.rsplit('.', 1)[1]  # .jpg
                name = u.make_name(work_name, i, file_format)
                futures_list.append(
                    executor.submit(u.down_file, url, name, path))
            if asset['asset_type'] == 'video' and self.b_is_down_video:
                url = re.findall(r'src="(.*?)"', asset['player_embedded'])[0]
                name = r'%s-%s' % (work_name, i+1)  # 这个很恶心，必须这样，否则无法创建文件，原因未知
                # name = r'new'
                print('这是个视频，下载比较忙，亲耐心等候。')
                futures_list.append(
                    executor.submit(u.down_youtube, url, name, path))
            if asset['asset_type'] == 'video_clip' and self.b_is_down_video:
                url = re.findall(r"src='(.*?)'", asset['player_embedded'])[0]
                r = u.session_get(url)
                source_media = re.findall(r'src="(.*?)" type=', r.text)[0]
                file_format = source_media.rsplit('.', 1)[1]  # .jpg
                name = u.make_name(work_name, i, file_format)
                print('这是个视频，下载比较忙，亲耐心等候。')
                print(source_media)
                futures_list.append(
                    executor.submit(u.down_file, source_media, name, path))
        futures.wait(futures_list)
        print("[正常]下载任务已完成；\n")

    def custom_name(self, j, file_name):
        if b_is_custom_name:
            username = j['user']['username']
            work_id = j['hash_id']
            file_name = file_name.rsplit('.', 1)
            return '{}-{}'.format(username, work_id)
        else:
            return file_name


class ZBrush:
    def __init__(self):
        self.b_is_down_video = True

    def get_work(self, url):
        print("ZB下载任务开始中，亲稍等，url：{}".format(url))
        r = u.session_get(url).text
        # 图片
        urls = re.findall(r'<img src="//(.*?).jpeg"', r)
        work_name = '{}-{}'.format(
            url.rsplit('/', 2)[1], url.rsplit('/', 2)[2])  # SwordGirl-402912
        path = u.make_save_path(work_name)
        u.check_make_dir(path)
        futures_list = []
        print('开始咯')
        for i, down_url in enumerate(urls):
            down_url = r'https://' + down_url + '.jpeg'
            name = u.make_name(work_name, i, 'jpeg')
            futures_list.append(
                executor.submit(u.down_file, down_url, name, path))
        # 视频
        if self.b_is_down_video:
            urls_video = re.findall(r'www(.*?)mp4', r)
            work_name = work_name + '_video'
            for i, video_url in enumerate(urls_video):
                video_url = 'https://www' + video_url + 'mp4'
                name = u.make_name(work_name, i, 'mp4')
                print('这是个视频，下载比较忙，亲耐心等候。')
                futures_list.append(
                    executor.submit(u.down_file, video_url, name, path))
        futures.wait(futures_list)
        print("[正常]下载任务已完成；\n")


class Utils:
    def __init__(self, log_print=None):
        if log_print:  # 好像是靠这个捕获打印。然后调用app.py里的函数。
            global print
            print = log_print

    def session_get(self, url):
        try:
            s = session.get(url)
            print('网络连接成功，正在分析数据，亲稍等。')
            return s
        except Exception as e:
            print('[错误]网络连接失败，错误：{};'.format(e))
            return

    def down_file(self, url, file_name, save_path):   # 下载图片
        '''下载输入的网址文件，并对其命名，保存到指定位置。
        :param url, str, 输入网页地址，如：https://cdna.artstation.com/p/1.jpg ;
        :param file_name, str, 文件保存名字，比如：awaw-5X9mYA-1.jpg ;
        :param save_path. str, 保存地址，比如：E:\asd '''
        r = session.get(url)  # 下载图片
        path = os.path.join(save_path, file_name)   # 保存路径和文件名字合并
        with open(path, 'wb') as f:
            f.write(r.content)
        print('完成下载，地址：{}'.format(url))

    def down_youtube(self, url, file_name, save_path):   # 下载视频
        '''下载输入的youtube网址，分析并下载，最后改名保存到指定路径。
        :param url, str, 输入网页地址，如https://www.youtube.com/watch?v=3uVvUD-5Vl4 ;
        '''
        save_path = save_path + "/"
        try:
            if file_name != '':
                YouTube(url).streams.first().download(save_path, file_name)
            else:
                print('下载很慢，请稍等！')
                YouTube(url).streams.first().download(save_path)
            print('完成下载，地址：{}'.format(url))
        except Exception as e:
            print(e)

    def down_video(self, url, path):
        print('下载较慢请稍等。')
        try:
            sys.argv = ['you-get', '-o', path, url]
            you_get.main()
            os.startfile(path)
            print('下载完成！')
        except Exception as e:
            print('下载错误，请自我检查，错误：{}'.format(e))

    def make_name(slef, name, index, format):
        '''通过输入的参数，合成名字，name1-name2-index.format
        :param index, int, 请输入0开始的，因为会自动+1'''
        return '{}-{}.{}'.format(name, index+1, format)

    def make_save_path(slef, name):
        '''输入名字并判断是否需要创建文件夹，最终制作保存路径'''
        if b_is_create_folder:
            return os.path.join(entry_path, name)
        return entry_path

    def check_make_dir(self, path):
        '''检查输入的路径是否有效，无效则尝试创建文件夹，最终成功后保存路径'''
        if os.path.exists(path):
            return True
        else:
            try:
                os.makedirs(path, exist_ok=True)
                print('保存地址：{}'.format(path))
                cf.save('base', 'save_path', path)
                return True
            except Exception as e:
                messagebox.showerror("错误", "请输入正确的文件夹路径！")
                print(e)
                return False


# 全局变量
u = Utils()
cf = config.Config('', 1, './')
b_is_create_folder = True
b_is_custom_name = True
entry_path = ''
# save_path = ''
session = requests.session()
executor = futures.ThreadPoolExecutor(cpu_count()*4)
executor_video = futures.ThreadPoolExecutor(1)


if __name__ == '__main__':
    url = 'https://www.artstation.com/artwork/5X9mYA'
    art = ArtStation()
    entry_path = r'D:\python\down'
    art.get_work(url)
    pass
