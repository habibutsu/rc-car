import asyncio
import logging

from aiohttp.web import (
    StreamResponse
)

logger = logging.getLogger()


def init(server):
    app = server.aiohttp_app
    app.router.add_get('/video', handle)


async def handle(request):
    server = request.app['server']
    car = server.car
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
            image = car.get_camera_image()
            response.write(b'--frame\r\n')
            response.write(b'Content-Type: image/jpeg\r\n\r\n')
            response.write(image.tobytes())
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
