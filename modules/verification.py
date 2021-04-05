from pathlib import Path
from re import compile, IGNORECASE, Pattern
from subprocess import run
from typing import Tuple, Mapping


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


def correct_version_is_installed(version_command: Tuple[str, ...], required_version: str) -> bool:
    """
    Checks whether the correct version of a program is installed.

    Args:
        version_command: The command that outputs the version of the program to stdout.
        required_version: The required version of the command in the form "<major>.<minor>.<release>"

    Returns:
        True if the current 'major' and 'minor' versions of the program are greater than or equal to the required ones.
    """
    version_regex: Pattern = compile(r'.*?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<release>\d+).*?')
    current_version_map: Mapping[str, int] = {
        label: int(version) for label, version in
        version_regex.match(
            run(version_command, capture_output=True, check=True).stdout.decode('utf-8')
        ).groupdict().items()
    }
    required_version_map: Mapping[str, int] = {
        label: int(version) for label, version in
        version_regex.match(required_version).groupdict().items()
    }

    return (
            current_version_map['major'] >= required_version_map['major']
            and
            current_version_map['minor'] >= required_version_map['minor']
    )
