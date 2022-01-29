import cherrypy
import os
from jinja2 import Environment, FileSystemLoader
from utils import download

env = Environment(loader=FileSystemLoader('html'), autoescape=True)

config = {

    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 80)),
    },

    '/assets': {
        'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'assets',
    },
    '/favicon.ico': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.ico")
    }
}


def process(func, arg):
    if func is None or arg is None:
        return None
    try:
        return func(arg)
    except Exception as e:
        print(e)


def render(template, func=None, arg=None):
    return env.get_template(template).render(data=process(func, arg))


class HomePage(object):

    @staticmethod
    @cherrypy.expose
    def index():
        return render("index.html")

    @staticmethod
    @cherrypy.expose
    def bhavcopy(date):
        return render("results.html", download, date)


root = HomePage()

if __name__ == '__main__':
    try:
        print("Starting...")
        cherrypy.quickstart(root, "/", config=config)
        print("Running..")
    except Exception as e:
        print("Exception")
        print(e)
