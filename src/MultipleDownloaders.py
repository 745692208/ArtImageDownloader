import sys
from app import App


title = 'Multiple Downloaders'
__version__ = "1.0.0"
suffix = ''


def main():
    app = App(title, __version__, suffix)
    app.app.mainloop()
    app.t.cancel()
    sys.exit()


if __name__ == '__main__':
    main()
