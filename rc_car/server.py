import asyncio
import logging
import os

import aiohttp.web

from aiohttp_index import IndexMiddleware

from .handlers import sys_stream
from .handlers import video_stream
from . import constants
from .model import Car

logger = logging.getLogger(__name__)


class Server:

    def __init__(self, cfg, loop=None):
        logger.info(
            'Service started on %s:%s with pid %s',
            cfg.server.host, cfg.server.port, os.getpid())
        self.cfg = cfg
        self.car = Car(cfg)

        self.loop = loop or asyncio.get_event_loop()
        self.aiohttp_app = aiohttp.web.Application(
            loop=self.loop,
            middlewares=[IndexMiddleware()]
        )
        self.aiohttp_app['server'] = self

        sys_stream.init(self)
        video_stream.init(self)

        self.aiohttp_app.router.add_static('/img/', constants.IMG_DIR)
        self.aiohttp_app.router.add_static('/js/', constants.JS_DIR)
        self.aiohttp_app.router.add_static('/', constants.HTML_DIR)

        async def init():
            handler = self.aiohttp_app.make_handler()
            srv = await self.loop.create_server(
                handler,
                host=self.cfg.server.host,
                port=self.cfg.server.port,
                backlog=self.cfg.server.backlog
            )
            self.aiohttp_app['http'] = {
                'handler': handler,
                'srv': srv
            }

        self.loop.run_until_complete(init())

    def stop(self):
        logger.info('Stopping server...')

        async def stop():
            self.car.close()
            app = self.aiohttp_app
            if 'http' in app:
                srv = app['http']['srv']
                handler = app['http']['handler']
                srv.close()
                await srv.wait_closed()
                await handler.shutdown(self.cfg.server.shutdown_timeout)
            await app.shutdown()
            await app.cleanup()
            self.loop.stop()
        return self.loop.create_task(stop())

    def reload(self):
        logger.info('Handle SIGHUP')

    def run_forever(self):
        try:
            self.loop.run_forever()
        finally:
            logger.info('Server was stopped')
