import asyncio
import time
import math
import logging

logger = logging.getLogger()


class DampingForward:

    def __init__(self, component):
        self.component = component
        self.is_running = True
        self._value = None

    def cancel(self):
        self.is_running = False
        self.component._value = self._value

    async def run(self, x, duration):
        self._value = x
        delta = duration / 20
        t = 0
        while t < duration and self.is_running:
            value = round(x + 1 / (0.6 * x) * math.exp(-t**2 / 3), 4)
            self.component._value = value
            self.component.motor.forward(
                value / self.component.scale
            )
            t += delta
            logger.debug('Updated value to %s...', value)
            await asyncio.sleep(delta)
        if self.is_running:
            self.component._value = x
            self.component.motor.forward(
                x / self.component.scale
            )


class Throttle:

    scale = 10

    def __init__(self):
        from gpiozero import Motor
        self.motor = Motor(23, 24)
        self._value = 0
        self._damping_task = None

    def register(self, vechicle):
        self._loop = vechicle.loop
        vechicle.commands['throttle'].append(self.throttle)
        vechicle.commands['stop'].append(self.stop)
        vechicle.sensors['throttle'] = self.value

    def value(self):
        return self._value

    def throttle(self, delta):
        if self._damping_task:
            self._damping_task.cancel()
            self._damping_task = None

        value = self._value + delta
        if value > self.scale or value < -self.scale:
            return

        if value >= 0:
            if delta > 0 and value > 0:
                self._damping_task = DampingForward(self)
                asyncio.ensure_future(
                    self._damping_task.run(value, 5),
                    loop=self._loop)
            else:
                self._value = value
                self.motor.forward(
                    value / self.scale
                )
        elif value < 0:
            self._value = value
            self.motor.backward(
                -value / self.scale
            )
        else:
            self.motor.stop()

    def stop(self, *args):
        if self._damping_task:
            self._damping_task.cancel()
            self._damping_task = None

        if self._value > 0:
            self._value = -1
            self.motor.backward(1)
        else:
            self._value = 1
            self.motor.forward(1)
        time.sleep(0.1)
        self._value = 0
        self.motor.stop()
