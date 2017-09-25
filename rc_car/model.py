from types import SimpleNamespace
import os
import logging

import cv2

from rc_car.constants import CAMERA_CLS


logger = logging.getLogger()


class Car:

    def __init__(self, cfg):
        self.cfg = cfg
        if self.cfg.model.use_mock:
            os.environ['GPIOZERO_PIN_FACTORY'] = 'mock'
            from gpiozero.pins.mock import MockPWMPin
            from gpiozero import Device
            Device.pin_factory.pin_class = MockPWMPin

        from gpiozero import Motor

        self.motor = Motor(23, 24)
        self.rudder = Motor(17, 27)
        self.camera = CAMERA_CLS[self.cfg.camera.type](
            self.cfg.camera.width, self.cfg.camera.height)
        logger.info('Using %s camera', self.camera)

        self.state = SimpleNamespace(
            accelerator=0,
            steering=0,
            speed=0,
            driving_mode='free',
        )

    def close(self):
        self.camera.release()

    def get_state(self):
        return vars(self.state)

    def get_camera_image(self, width, height):
        image = self.camera.read()
        result, jpg_image = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 60])
        return jpg_image

    def accelerate(self, value):
        accelerator = self.state.accelerator + value
        if accelerator > 10 or accelerator < -10:
            return

        self.state.accelerator = accelerator
        if accelerator > 0:
            self.motor.forward(
                accelerator / 10
            )
        elif accelerator < 0:
            self.motor.backward(
                -accelerator / 10
            )
        else:
            self.motor.stop()

    def drive(self, value):
        steering = self.state.steering + value
        if steering > 10 or steering < -10:
            return

        self.state.steering = steering
        if self.state.steering > 0:
            self.rudder.forward(
                self.state.steering / 10
            )
        elif self.state.steering < 0:
            self.rudder.backward(
                -self.state.steering / 10
            )
        else:
            self.rudder.stop()

    def stop(self):
        if self.state.accelerator > 0:
            self.motor.backward(1)
        else:
            self.motor.forward(1)
        self.state.accelerator = 0
        self.state.steering = 0
        self.motor.stop()
        self.rudder.stop()
