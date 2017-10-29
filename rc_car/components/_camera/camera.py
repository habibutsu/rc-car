import datetime
import logging
import ctypes
import time
from threading import Thread
from multiprocessing import Array, Process, Event

import numpy as np
import cv2


logger = logging.getLogger('rc-car')


class USBCamera:

    def __init__(self, width, height, framerate=25):
        self.width = width
        self.height = height
        self.camera = cv2.VideoCapture(0)

    def read(self):
        _result, image = self.camera.read()
        image = cv2.resize(image, (self.width, self.height))
        return image

    def release(self):
        self.camera.release()


class AstractProcessCamera:
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


class USBProcessCamera(AstractProcessCamera):

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


class PiThreadCamera:

    def __init__(self, width, height, framerate=25):
        import picamera
        import picamera.array
        self.width = width
        self.height = height
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.width, self.height)
        self.camera.framerate = framerate
        self.raw_capture = picamera.array.PiRGBArray(
            self.camera, size=(self.width, self.height))
        self.stream = self.camera.capture_continuous(
            self.raw_capture, format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
        # start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        logger.info('Start streaming from camera')
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.raw_capture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.raw_capture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        # image = cv2.resize(self.frame, (self.width, self.height))
        return self.frame

    def release(self):
        # indicate that the thread should be stopped
        self.stopped = True
        logger.info('Wait camera thread')
        self.thread.join()


class PiProcessCamera(AstractProcessCamera):

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


class PiCamera:

    def __init__(self, width, height, framerate=25):
        import picamera
        self.width = width
        self.height = height
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.width, self.height)
        self.camera.framerate = framerate
        time.sleep(1)

    def read(self):
        output = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.camera.capture(output, 'bgr')
        return output

    def release(self):
        self.camera.close()


class MockCamera:

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
