import logging
import os

logger = logging.getLogger()


_FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'frontend')
HTML_DIR = os.path.join(_FRONTEND_DIR, 'html')
JS_DIR = os.path.join(_FRONTEND_DIR, 'js')
IMG_DIR = os.path.join(_FRONTEND_DIR, 'img')


class FrontEnd:

    def register(self, server):
        app = server.aiohttp_app
        app.router.add_static('/img/', IMG_DIR)
        app.router.add_static('/js/', JS_DIR)
        app.router.add_static('/', HTML_DIR)
