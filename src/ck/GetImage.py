"""
GetImage

"""
import requests
import time
import os

def down_images(urls, dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    for url in urls:
        #time.sleep(1)
        down_image(url, dir_name)

def down_image(url, dir_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'}
    proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
    #url = 'https://cdnb.artstation.com/p/assets/images/images/035/526/835/4k/alex-beddows-balls.jpg'

    r = requests.get(url, headers=headers, proxies=proxies)
    print(r.status_code)

    file_name = url.split('/')[-1]
    with open(dir_name + '/' + file_name, 'wb') as f:
        f.write(r.content)
