"""
This module contains validation rules used throughout the project.
"""

import re
from pathlib import Path


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
