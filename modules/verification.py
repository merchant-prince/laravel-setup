"""
This module contains validation rules used throughout the project.
"""

from re import compile, IGNORECASE, sub
from pathlib import Path
from subprocess import run
from typing import Tuple


def is_pascal_case(string: str) -> bool:
    return compile(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$').match(string) is not None


def domain_is_valid(domain: str) -> bool:
    return compile(
        r'^'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'  # domain
        r'(?:/?|[/?]\S+)'  # path
        r'$',
        IGNORECASE
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


def correct_docker_compose_version_is_installed(required_version: Tuple[int, ...]) -> bool:
    """
    Checks if the correct docker-compose version is installed on the system.

    Args:
        required_version: A tuple of 2 ints representing the required major and minor versions of docker-compose for the
                          project.

    Returns:
        True if the current version of docker-compose is equal to or greater than the required version.
    """
    current_version: Tuple[int, ...] = tuple(
        int(v) for v in
        run(
            ('docker-compose', 'version', '--short'),
            capture_output=True,
            check=True
        ).stdout.decode('utf-8').strip().split('.')[:2]
    )

    return current_version >= required_version


def correct_openssl_version_is_installed(required_version: Tuple[int, ...]) -> bool:
    """
    Checks if the correct openssl version is installed on the system.

    Args:
        required_version: A tuple of 3 ints representing the required major, minor, and release versions of openssl for
                          the project.

    Returns:
        True if the current version of openssl is equal to or greater than the required version.
    """
    current_version: Tuple[int, ...] = tuple(
        int(sub(r'\D', '', v)) for v in
        run(
            ('openssl', 'version'),
            capture_output=True,
            check=True
        ).stdout.decode('utf-8').strip().split(' ')[1].split('.')
    )

    return current_version >= required_version


def correct_git_version_is_installed(required_version: Tuple[int, ...]) -> bool:
    """
    Checks if the correct git version is installed on the system.

    Args:
        required_version: A tuple of 3 ints representing the required major and minor versions of git for the project.

    Returns:
        True if the current version of git is equal to or greater than the required version.
    """
    current_version: Tuple[int, ...] = tuple(
        int(v) for v in
        run(
            ('git', 'version'),
            capture_output=True,
            check=True
        ).stdout.decode('utf-8').strip().split(' ')[-1].split('.')[:2]
    )

    return current_version >= required_version
