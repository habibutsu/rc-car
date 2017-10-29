

class Rudder:

    scale = 10

    def __init__(self):
        from gpiozero import Motor
        self.motor = Motor(17, 27)
        self._value = 0

    def register(self, vechicle):
        vechicle.commands['rudder'].append(self.rudder)
        vechicle.commands['stop'].append(self.stop)
        vechicle.sensors['rudder'] = self.value

    def value(self):
        return self._value

    def rudder(self, delta):
        value = self._value + delta
        if value > self.scale or value < -self.scale:
            return

        self._value = value
        if value > 0:
            self.motor.forward(
                value / self.scale
            )
        elif value < 0:
            self.motor.backward(
                -value / self.scale
            )
        else:
            self.motor.stop()

    def stop(self, *args):
        self._value = 0
        self.motor.stop()
