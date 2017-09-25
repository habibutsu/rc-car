import asyncio
import logging

import ujson as json

from aiohttp.web import (
    Response,
    WebSocketResponse,
    WSMsgType
)

from rc_car.utils import make_periodic_task

logger = logging.getLogger()


async def stream_state(server):

    for ws_client in server.aiohttp_app['ws_clients']:
        logger.debug('Send state to %s', id(ws_client))
        await ws_client.send_str(
            json.dumps({
                'result': 'ok',
                'state': server.car.get_state()
            })
        )


def init(server):
    app = server.aiohttp_app
    app.router.add_get('/sys', wshandler)
    app['ws_clients'] = []
    app['task'] = make_periodic_task(
        asyncio.coroutine(lambda: stream_state(server)),
        app.loop,
        3
    )
    app.on_shutdown.append(on_shutdown)


async def wshandler(request):
    server = request.app['server']
    ws_client = WebSocketResponse()
    ok, protocol = ws_client.can_prepare(request)
    if not ok:
        return Response(body=b"invalid connection", content_type='text/html')

    await ws_client.prepare(request)

    try:
        logger.info('Someone joined.')
        request.app['ws_clients'].append(ws_client)

        async for raw_msg in ws_client:
            if raw_msg.type == WSMsgType.TEXT:
                try:
                    msg = json.loads(raw_msg.data)
                    logger.debug('incomming msg: %s', msg)
                    # TODO
                    cmd = msg['cmd']
                    if cmd in "accelerate":
                        server.car.accelerate(msg['value'])
                    elif cmd in "drive":
                        server.car.drive(msg['value'])
                    elif cmd in "stop":
                        server.car.stop()
                    else:
                        logger.info('unknow command %s', cmd)
                    await ws_client.send_str(
                        json.dumps({
                            'result': 'ok',
                            'state': server.car.get_state()
                        })
                    )
                except Exception as e:
                    logger.exception('invalid message %s', raw_msg.data)
                    await ws_client.send_str(
                        json.dumps({
                            'result': 'error',
                            'message': str(e)
                        })
                    )
            else:
                return ws_client
        return ws_client

    finally:
        request.app['ws_clients'].remove(ws_client)
        logger.info('Someone disconnected.')


async def on_shutdown(app):
    for ws in app['ws_clients']:
        await ws.close()
