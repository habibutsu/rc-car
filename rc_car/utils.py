import asyncio
import logging
import traceback
import configparser
import time

from contextlib import contextmanager
from types import SimpleNamespace
from collections import Counter


@contextmanager
def track_time():
    start = time.time()
    elapsed = lambda: time.time() - start
    yield lambda: elapsed()
    end = time.time()
    elapsed = lambda: end - start


def load_config(default_cfg, config_file=None):
    config_parser = configparser.ConfigParser()
    if config_file:
        config_parser.read_file(config_file)

    cfg_dict = {}
    for section, default in default_cfg.items():
        section_obj = config_parser[section] if section in config_parser else {}
        cfg_dict[section] = {}
        for key, default_value in default.items():
            if key in section_obj:
                value = default_value[1](section_obj[key])
                if value is None:
                    raise RuntimeError('Incorrectly configured {}/{}'.format(section, key))
            else:
                value = default_value[0]
            cfg_dict[section][key] = value
        cfg_dict[section] = SimpleNamespace(**cfg_dict[section])

    cfg = SimpleNamespace(**cfg_dict)
    # # update log level
    # for logger in LOGGING.get('loggers', {}).values():
    #     logger['level'] = cfg.server.log_level.upper()
    # logging.config.dictConfig(LOGGING)
    return cfg


class OneLineExceptionFormatter(logging.Formatter):
    '''
        Formatter for logging exceptions in one line
    '''

    def formatException(self, exc_info):
        exc_type, exc_value, exc_traceback = exc_info
        tb = traceback.extract_tb(exc_traceback)
        tb_fmt = ' | '.join([
            f'File "{frame.filename}", line {frame.lineno}, in {repr(frame.line)}'
            for frame in tb
        ])
        return f' | {exc_type.__name__} | {exc_value} |{tb_fmt}'

    def format(self, record):
        s = super().format(record)
        if record.exc_text:
            # for preventing separation of 'exception' from message
            s = s.replace('\n', '')
        return s


class EventLoopMonitor:
    '''
        Monitoring tasks and latency of given event loop
    '''

    def __init__(self, loop, interval=3):
        self._interval = interval
        self.loop = loop
        self.latency = 0
        self.tasks_statistic = {}
        self.run()

    def run(self):
        self.loop.call_later(self._interval, self._handler, self.loop.time())

    def _handler(self, start_time):
        self.latency = (self.loop.time() - start_time) - self._interval

        all_tasks = asyncio.Task.all_tasks(loop=self.loop)
        tasks_statistic = dict(Counter([
            # (name, state)
            (str(t._coro).split()[2], t._state.lower())
            for t in all_tasks
        ]).most_common())

        zero_keys = set(self.tasks_statistic.keys()) - set(tasks_statistic.keys())
        for key in zero_keys:
            self.tasks_statistic[key] = 0

        self.tasks_statistic.update(tasks_statistic)

        self.run()


def make_periodic_task(fn, loop, delay):
    async def _run():
        while True:
            await fn()
            await asyncio.sleep(delay, loop=loop)

    return asyncio.ensure_future(_run(), loop=loop)
