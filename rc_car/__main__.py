import argparse
import logging.config
import sys
import logging

from rc_car.utils import load_config
from rc_car.vechicle import Vechicle
from rc_car.components.throttle import Throttle
from rc_car.components.rudder import Rudder
from rc_car.components.sys_bus import SysBus
from rc_car.components.frontend import FrontEnd
from rc_car.components.radar import Radar
from rc_car.components.accelerometer import Accelerometer
from rc_car.components.camera import CAMERA_CLS, Camera
from rc_car.components.control_block import ControlBlock
from rc_car.components.headlamp import HeadLamp


DEFAULT_CFG = dict(
    server=dict(
        log_level=('info', lambda x: x if x in ['info', 'debug', 'error'] else None),
        host=('0.0.0.0', str),
        port=(9000, int),
        backlog=(128, int),
        shutdown_timeout=(2, int),
        data_dir=('./data', str),
    ),
    model=dict(
        use_mock=(False, lambda x: x.lower() == 'true' if isinstance(x, str) else x),
    ),
    camera=dict(
        framerate=(20, int),
        type=('picamera', lambda x: x if x in CAMERA_CLS else None),
        # width=(160, int),
        # height=(128, int),
        width=(320, int),
        height=(240, int)
    )
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # 'class': 'rc_car.utils.OneLineExceptionFormatter',
            'format': '%(levelname)s | %(asctime)s | %(name)s | %(message)s',
        },
        'simple': {
            'format': '%(levelname)s | %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
}


def main(argv):
    arg_parser = argparse.ArgumentParser(
        description="Server represented of RC-car",
        prog="rc_car"
    )
    arg_parser.add_argument(
        "-c", "--config",
        type=argparse.FileType('r'),
        help='Config file')

    parsed_args = arg_parser.parse_args(argv)

    cfg = load_config(DEFAULT_CFG, parsed_args.config)
    # update log level
    for logger in LOGGING.get('loggers', {}).values():
        logger['level'] = cfg.server.log_level.upper()
    logging.config.dictConfig(LOGGING)

    vechicle = Vechicle(cfg)
    vechicle.add_component('camera', Camera())
    vechicle.add_component('throttle', Throttle())
    vechicle.add_component('rudder', Rudder())
    vechicle.add_component('sysbus', SysBus())
    vechicle.add_component('frontend', FrontEnd())
    vechicle.add_component('radar', Radar())
    vechicle.add_component('accelerometer', Accelerometer())
    vechicle.add_component('control_block', ControlBlock())
    vechicle.add_component('headlamp', HeadLamp())
    vechicle.run_forever()


if __name__ == '__main__':
    main(sys.argv[1:])
