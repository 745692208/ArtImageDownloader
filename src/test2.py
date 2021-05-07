import requests
import time
class Core:
    def __init__(self):
        self.session = requests.session()
        
    def get_projects(self):
        url = 'https://www.artstation.com/users/jay_howse/projects.json?page=0'
        r = session.get(url)
        print(r)

a = Core()
a.get_projects()