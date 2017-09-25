import os
import sys
import datetime as dt
from setuptools import setup


MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON:
    sys.stderr.write("Python {}.{} or later is required\n".format(*MIN_PYTHON))
    sys.exit(1)


with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as fd:
    requirements = [l.strip() for l in fd.readlines()]


setup(
    name='rc-car',
    #version='0.1.{}'.format(dt.datetime.now().strftime('%Y%m%d')),
    version='0.1',
    description='RC-car server',
    author='Alexander Verbitskiy',
    author_email='habibutsu@gmail.com',
    license=license,
    packages=['rc_car'],
    package_data={
        'rc_car': [
            '../requirements.txt',
            'handlers/*.py',
            'frontend/elm-package.json',
            'frontend/package.json',
            'frontend/app/*.*',
            'frontend/html/*.*',
            'frontend/img/*.*',
            'frontend/js/*.*'
        ],
    },
    test_suite='test',
    install_requires=requirements,
)
