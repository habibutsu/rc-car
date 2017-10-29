import asyncio
import logging
import os
import signal
from collections import defaultdict

import aiohttp.web
from aiohttp_index import IndexMiddleware


logger = logging.getLogger('rc-car.vechicle')


class Vechicle:

    DEFAULT_CFG = {}

    def __init__(self, cfg=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.cfg = cfg

        if self.cfg.model.use_mock:
            logger.info('Use mock-factory...')
            os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'
            from gpiozero.pins.mock import MockPWMPin
            from gpiozero import Device
            Device.pin_factory.pin_class = MockPWMPin

        self.commands = defaultdict(list)
        self.sensors = defaultdict(list)
        self.parameters = defaultdict(list)
        self.components = {}

        self.init_signals()
        self.init_aiohttp_app()

    def init_signals(self):
        for sig in ('SIGINT', 'SIGTERM'):
            self.loop.add_signal_handler(getattr(signal, sig), self.stop)
            self.loop.add_signal_handler(signal.SIGHUP, self.reload)
            signal.siginterrupt(signal.SIGTERM, False)

    def init_aiohttp_app(self):
        self.aiohttp_app = aiohttp.web.Application(
            loop=self.loop,
            middlewares=[
                IndexMiddleware()
            ]
        )
        self.aiohttp_app['server'] = self

    def stop(self):
        logger.info('Stopping server...')

        async def stop():
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

    def add_component(self, name, component):
        component.register(self)
        self.components[name] = component

    def get_state(self):
        sensors = {
            name: value()
            for name, value in self.sensors.items()
        }
        parameters = {
            name: value()
            for name, value in self.parameters.items()
        }
        return {
            'sensors': sensors,
            'parameters': parameters
        }

    def run_forever(self):
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
        logger.info(
            'Service started on %s:%s with pid %s',
            self.cfg.server.host, self.cfg.server.port, os.getpid())
        try:
            self.loop.run_forever()
        finally:
            logger.info('Server was stopped')
