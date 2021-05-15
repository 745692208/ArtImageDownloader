# -*- coding: utf-8 -*-

import sys

"""
批量下载ArtStation图片
"""

__version__ = "1.1.0"

from app import App


def main():
    app = App(version=__version__)  # 运行GUI
    app.mainloop()  # 进入主循环，程序运行
    app.t.cancel()
    app.quit()
    sys.exit()


if __name__ == '__main__':
    main()
