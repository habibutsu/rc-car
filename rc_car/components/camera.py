import asyncio
import logging
import datetime
import ctypes
import time
from multiprocessing import Array, Process, Event

from aiohttp.web import (
    StreamResponse
)

import numpy as np
import cv2

logger = logging.getLogger()


class AstractProcessCameraDevice:
    '''
        polling the camera in separate process
    '''

    def __init__(self, width, height, framerate):
        self.width = width
        self.height = height
        self.framerate = framerate
        self.is_running = Event()
        self.is_running.set()
        self._shared_array = Array(ctypes.c_uint8, [0] * (width * height * 3))
        self._image = self.get_numpy_array(self._shared_array, self.width, self.height)
        # fill with zeros
        self._image[:] = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self._process = Process(
            target=self.update,
            args=(self.is_running, self._shared_array,
                  self.width, self.height, self.framerate))
        self._process.start()

    @classmethod
    def get_numpy_array(cls, shared_array, width, height):
        shared_numpy_array = np.frombuffer(shared_array.get_obj(), dtype=np.uint8)
        return shared_numpy_array.reshape((height, width, 3))

    @classmethod
    def update(cls, is_running, shared_array, width, height, framerate):
        raise NotImplementedError

    def read(self):
        with self._shared_array.get_lock():
            return self._image.copy()

    def release(self):
        self.is_running.clear()
        self._process.join()


class USBProcessCameraDevice(AstractProcessCameraDevice):

    @classmethod
    def update(cls, is_running, shared_array, width, height, framerate):
        camera = cv2.VideoCapture(0)
        shared_image = cls.get_numpy_array(shared_array, width, height)
        try:
            while is_running.is_set():
                with shared_array.get_lock():
                    _result, image = camera.read()
                    image = cv2.resize(image, (width, height))
                    shared_image[:] = image
                time.sleep(1 / 60)
        except KeyboardInterrupt as e:
            pass
        finally:
            camera.release()


class PiProcessCameraDevice(AstractProcessCameraDevice):

    @classmethod
    def update(cls, is_running, shared_array, width, height, framerate):
        import gc
        import picamera
        import picamera.array
        gc.disable()
        logger.info('init camera...')
        camera = picamera.PiCamera()
        camera.resolution = (width, height)
        camera.framerate = framerate
        raw_capture = picamera.array.PiRGBArray(
            camera, size=(width, height))
        stream = camera.capture_continuous(
            raw_capture, format="bgr", use_video_port=True)

        shared_image = cls.get_numpy_array(shared_array, width, height)
        try:
            frame = None
            for f in stream:
                frame = f.array
                raw_capture.truncate(0)
                # frame = cv2.resize(frame, (width, height))
                with shared_array.get_lock():
                    shared_image[:] = frame
                if not is_running.is_set():
                    return
                time.sleep(1 / 60)
        except KeyboardInterrupt as e:
            pass
        except Exception as e:
            logger.exception(e)
        finally:
            stream.close()
            raw_capture.close()
            camera.close()
            return


class MockCameraDevice:

    def __init__(self, width, height, framerate=25):
        self.width = width
        self.height = height

    def read(self):
        font_weight = 2
        font_size = 1
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_lines = [
            'No signal',
            datetime.datetime.now().strftime('%H:%M:%S')
        ]
        image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        dy = 40 * int(len(text_lines) * 0.5)
        for num, text in enumerate(text_lines):
            cv2.putText(
                image, text,
                (int(self.width * 0.5) - 70, int(self.height * 0.5) - dy + num * 40),
                font, font_size, (255, 255, 255), font_weight)
        return image

    def release(self):
        pass


class Camera:

    def register(self, server):
        app = server.aiohttp_app
        app.router.add_get('/video', self.handle)
        self.camera = CAMERA_CLS[server.cfg.camera.type](
            server.cfg.camera.width,
            server.cfg.camera.height,
            server.cfg.camera.framerate
        )
        logger.info('Using %s camera', self.camera)

        app.on_shutdown.append(self.on_shutdown)

    async def on_shutdown(self, app):
        self.camera.release()

    async def handle(self, request):
        server = request.app['server']
        _width = int(request.query.get('width', 1280))      # noqa: F841
        _height = int(request.query.get('height', 720))     # noqa: F841
        response = StreamResponse()
        response.headers['Content-Type'] = 'multipart/x-mixed-replace; boundary=frame'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        # response.enable_chunked_encoding()
        await response.prepare(request)

        while True:
            try:
                image = self.camera.read()
                _result, jpg_image = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 60])

                response.write(b'--frame\r\n')
                response.write(b'Content-Type: image/jpeg\r\n\r\n')
                response.write(jpg_image.tobytes())
                response.write(b'\r\n')
                await response.drain()
                await asyncio.sleep(1 / server.cfg.camera.framerate)
            except asyncio.CancelledError as e:
                break
            except Exception as e:
                # https://github.com/aio-libs/aiohttp/issues/1893
                logger.exception(e)
                break

        await response.write_eof()
        return response


CAMERA_CLS = {
    'mock': MockCameraDevice,
    'picamera': PiProcessCameraDevice,
    'usb': USBProcessCameraDevice
}
