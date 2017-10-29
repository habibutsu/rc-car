import asyncio
import logging
import os
from datetime import datetime

import joblib

from rc_car.utils import track_time

logger = logging.getLogger()


class DrivingMode:

    free = 'free'
    record = 'record'
    self = 'self'


class ControlBlock:
    '''
        Component that responds for controlling and working
        the car in corresponded of working mode
    '''

    def __init__(self):
        self._mode = DrivingMode.free
        self._delay = 3

    def register(self, vechicle):
        self.vechicle = vechicle
        vechicle.commands['mode'].append(self.set_mode)
        vechicle.commands['delay'].append(self.set_delay)
        vechicle.parameters['mode'] = self.get_mode
        vechicle.parameters['delay'] = self.get_delay

    def get_mode(self):
        return self._mode

    def get_delay(self):
        return self._delay

    def set_delay(self, delay):
        try:
            self._delay = int(delay)
        except:
            self._delay = None

    def set_mode(self, mode, delay=None):
        logger.info('Update mode %s', mode)
        self._mode = mode
        if mode == DrivingMode.record:
            self.vechicle.loop.create_task(self.recording())
        # TODO: if mode self -> use ML for control the car

    async def recording(self):
        framerate = 5
        remain = self._delay * framerate
        frame = 0
        while remain:
            with track_time() as elapsed:
                utc_now = datetime.utcnow()
                filename = os.path.join(
                    self.vechicle.cfg.server.data_dir,
                    utc_now.strftime('%Y-%m-%d_%H-%M-%S_{}.dat'.format(frame)))
                with open(filename, 'wb') as fd:
                    img = self.vechicle.components['camera'].camera.read()
                    state = self.vechicle.get_state()
                    joblib.dump((img, state), fd)
            logger.debug('write frame in %s', elapsed())
            await asyncio.sleep(1 / framerate, loop=self.vechicle.loop)
            remain -= 1
            frame += 1
        self._mode = DrivingMode.free
