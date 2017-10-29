import logging
import time
from multiprocessing import Value, Process, Event

logger = logging.getLogger('rc-car')


class Radar:

    def __init__(self):
        self._value = Value('d', 0.0)
        self.is_running = Event()
        self.is_running.set()
        self._process = Process(
            target=self.update, args=(self.is_running, self._value))

    def register(self, vechicle):
        vechicle.sensors['radar'] = self.value
        self._process.start()
        app = vechicle.aiohttp_app
        app.on_shutdown.append(self.on_shutdown)

    def value(self):
        return self._value.value

    @classmethod
    def update(cls, is_running, share_value):
        from gpiozero import DistanceSensor
        sensor = DistanceSensor(echo=18, trigger=4, max_distance=5)
        try:
            while is_running.is_set():
                share_value.value = sensor.distance
                time.sleep(1 / 60)
        except KeyboardInterrupt as e:
            pass

    def on_shutdown(self, app):
        logger.info('Stopping radar')
        self.is_running.clear()
        self._process.join()
