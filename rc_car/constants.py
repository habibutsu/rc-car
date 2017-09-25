import os

from rc_car.components import camera


_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')
HTML_DIR = os.path.join(_FRONTEND_DIR, 'html')
JS_DIR = os.path.join(_FRONTEND_DIR, 'js')
IMG_DIR = os.path.join(_FRONTEND_DIR, 'img')

CAMERA_CLS = {
    'mock': camera.MockCamera,
    'picamera': camera.PiProcessCamera,
    'usb': camera.USBProcessCamera
}

DEFAULT_CFG = dict(
    server=dict(
        log_level=('info', lambda x: x if x in ['info', 'debug', 'error'] else None),
        host=('0.0.0.0', str),
        port=(9000, int),
        backlog=(128, int),
        shutdown_timeout=(2, int),
    ),
    model=dict(
        use_mock=(False, lambda x: x.lower() == 'true' if isinstance(x, str) else x),
    ),
    camera=dict(
        type=('picamera', lambda x: x if x in CAMERA_CLS else None),
        width=(480, int),
        height=(270, int),
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
