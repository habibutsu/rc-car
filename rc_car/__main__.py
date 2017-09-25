import argparse
import logging.config
import signal
import sys
import configparser

from rc_car.server import Server
from rc_car.utils import processing_confg
from rc_car.constants import LOGGING


def main(argv):
    arg_parser = argparse.ArgumentParser(
        description="Application for snatching of Uber-surges",
        prog="rc-car"
    )
    arg_parser.add_argument(
        "-C", "--config",
        type=argparse.FileType('r'),
        help='Config file')

    parsed_args = arg_parser.parse_args(argv)
    config_parser = configparser.ConfigParser()

    if parsed_args.config:
        config_parser.read_file(parsed_args.config)

    cfg = processing_confg(config_parser)

    # update log level
    for logger in LOGGING.get('loggers', {}).values():
        logger['level'] = cfg.server.log_level.upper()
    logging.config.dictConfig(LOGGING)

    server = Server(cfg)
    for sig in ('SIGINT', 'SIGTERM'):
        server.loop.add_signal_handler(getattr(signal, sig), server.stop)
    server.loop.add_signal_handler(signal.SIGHUP, server.reload)
    signal.siginterrupt(signal.SIGTERM, False)

    server.run_forever()


if __name__ == '__main__':
    main(sys.argv[1:])
