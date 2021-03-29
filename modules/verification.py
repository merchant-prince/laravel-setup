"""
This module contains validation rules used throughout the project.
"""

import re
from pathlib import Path
from subprocess import run
from typing import Tuple


def is_pascal_case(string: str) -> bool:
    return re.compile(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$').match(string) is not None


def domain_is_valid(domain: str) -> bool:
    return re.compile(
        r'^'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'  # domain
        r'(?:/?|[/?]\S+)'  # path
        r'$',
        re.IGNORECASE
    ).match(domain) is not None


def directory_exists(name: str) -> bool:
    return Path(name).is_dir()


def correct_docker_version_is_installed(required_version: Tuple[int, ...]) -> bool:
    """
    Checks if the correct docker version is installed on the system.

    Args:
        required_version: A tuple of 2 ints representing the required major and minor versions of docker for the
                          project.

    Returns:
        True if the current version of docker is equal to or greater than the required version.
    """
    current_version: Tuple[int, ...] = tuple(
        int(v) for v in
        run(
            ('docker', 'version', '--format', '{{.Server.Version}}'),
            capture_output=True,
            check=True
        ).stdout.decode('utf-8').strip().split('.')[:2]
    )

    return current_version >= required_version
