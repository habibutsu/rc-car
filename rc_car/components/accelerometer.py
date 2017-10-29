# http://we.easyelectronics.ru/pilamaster/raspberry-pi-rabotaem-s-i2c-na-python.html
# http://blog.bitify.co.uk/2013/11/interfacing-raspberry-pi-and-mpu-6050.html
# http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html

import logging
import time
from multiprocessing import Array, Process, Event

logger = logging.getLogger('rc-car')


class Accelerometer:

    def __init__(self):
        self._value = Array('d', range(3))
        self.is_running = Event()
        self.is_running.set()
        self._process = Process(
            target=self.update, args=(self.is_running, self._value))

    def register(self, vechicle):
        vechicle.sensors['accelerometer'] = self.value
        self._process.start()
        app = vechicle.aiohttp_app
        app.on_shutdown.append(self.on_shutdown)

    def value(self):
        return self._value[:].copy()

    @classmethod
    def update(cls, is_running, shared_value):
        from mpu6050 import mpu6050
        sensor = mpu6050(0x68)
        try:
            while is_running.is_set():
                # https://arduino.stackexchange.com/questions/22798/can-i-measure-velocity-from-an-accelerometer-how-accurately
                # http://www.chrobotics.com/library/accel-position-velocity
                # https://www.i2cdevlib.com/forums/topic/312-velocity-from-acceleration/
                # gyro_data = sensor.get_gyro_data()
                # temp = sensor.get_temp()
                accel_data = sensor.get_accel_data()
                with shared_value.get_lock():
                    shared_value[0] = round(accel_data['x'], 4)
                    shared_value[1] = round(accel_data['y'], 4)
                    shared_value[2] = round(accel_data['z'], 4)
                # with shared_value.get_lock():
                #     for i in range(len(shared_value)):
                #         shared_value[i] = round(random.random()*100, 2)
                time.sleep(1 / 60)
        except KeyboardInterrupt as e:
            pass

    def on_shutdown(self, app):
        logger.info('Stopping accelerometer...')
        self.is_running.clear()
        self._process.join()
