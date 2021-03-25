#!/usr/bin/env python3

import logging
import sys


REQUIRED_PYTHON_VERSION = '3.9'
REQUIRED_PIP_VERSION = '20.3'


def current_python_version_is_less_than(required_version: str) -> bool:
    """
    Checks if the current version of python is less than the required version.

    Args:
        required_version: the required version of python.

    Returns:
        A boolean corresponding to whether the current version of python is less than the required one.
    """
    current_version_major, current_version_minor = sys.version_info[:2]
    required_version_major, required_version_minor, *_ = (int(s) for s in required_version.split('.'))

    return (current_version_major < required_version_major) or (current_version_minor < required_version_minor)


def current_pip_version_is_less_than(required_version: str) -> bool:
    """
    Checks if the current version of pip is less than the required version.

    Args:
        required_version: the required version of pip.

    Returns:
        A boolean corresponding to whether the current version of pip is less than the required one.
    """
    try:
        import pip

        current_version_major, current_version_minor, *_ = (int(s) for s in pip.__version__.split('.'))
        required_version_major, required_version_minor, *_ = (int(s) for s in required_version.split('.'))

        return (current_version_major < required_version_major) or (current_version_minor < required_version_minor)

    except ImportError as error:
        logging.error(f'Pip is not installed. {error}')
        exit(64)


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s: %(msg)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )

    if current_python_version_is_less_than(REQUIRED_PYTHON_VERSION):
        logging.error(f'The current python version is less than {REQUIRED_PYTHON_VERSION}.')
        exit(64)

    logging.info('Python version: OK')

    if current_pip_version_is_less_than(REQUIRED_PIP_VERSION):
        logging.warning(f'The current pip version is less than {REQUIRED_PIP_VERSION}.')
        logging.warning('Pip version: NOT OK')
    else:
        logging.warning('Pip version: OK')
