import logging

logger = logging.getLogger('rc-car')


class State:

    on = 'on'
    off = 'off'


class HeadLamp:

    def __init__(self):
        self._state = State.off
        from gpiozero import LED
        self.left_led = LED(12)
        self.right_led = LED(26)

    def register(self, vechicle):
        self.vechicle = vechicle
        vechicle.commands['headlamp'].append(self.set_state)
        vechicle.parameters['headlamp'] = self.get_state

    def get_state(self):
        return self._state

    def set_state(self, state):
        logger.info('Update state %s', state)
        if state == State.on:
            self.left_led.on()
            self.right_led.on()
        else:
            self.left_led.off()
            self.right_led.off()
        self._state = state
