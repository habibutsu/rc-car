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


class SysBus:

    def register(self, vechicle):
        app = vechicle.aiohttp_app
        app.router.add_get('/sys', wshandler)
        app['ws_clients'] = []
        app['task'] = make_periodic_task(
            asyncio.coroutine(lambda: stream_state(vechicle)),
            app.loop,
            1 / 4
        )
        app.on_shutdown.append(on_shutdown)


async def on_shutdown(app):
    for ws in app['ws_clients']:
        await ws.close()
    app['task'].cancel()


async def stream_state(vechicle):
    try:
        for ws_client in vechicle.aiohttp_app['ws_clients']:
            state = vechicle.get_state()
            # sensors = {
            #     name: value()
            #     for name, value in server.sensors.items()
            # }
            # parameters = {
            #     name: value()
            #     for name, value in server.parameters.items()
            # }
            # data = {
            #     'result': 'ok',
            #     'sensors': sensors,
            #     'parameters': parameters
            # }
            state['result'] = 'ok'
            logger.debug('Send state %s to %s', state, id(ws_client))
            await ws_client.send_str(
                json.dumps(state)
            )
    except Exception as e:
        logger.exception(e)


async def wshandler(request):
    vechicle = request.app['server']
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
                    cmd = msg['cmd']
                    if cmd in vechicle.commands:
                        for action in vechicle.commands[cmd]:
                            action(msg['arg1'])
                    else:
                        logger.info('unknow command %s', cmd)
                    await stream_state(vechicle)

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
