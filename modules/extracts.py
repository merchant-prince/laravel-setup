"""
This module contains code extracted from other scripts (mostly main.py)
"""

from argparse import ArgumentParser, Namespace
from typing import Mapping

from modules.scaffolding import directory_structure_is_valid, create_directory_structure
from modules.verification import correct_version_is_installed, directory_exists, domain_is_valid, is_pascal_case


def preliminary_checks(*, requirements: Mapping[str, str]) -> None:
    """
    Checks whether the correct version of the dependencies of the script are installed.

    Args:
        requirements: Versions of the dependencies
    """
    if not correct_version_is_installed(
            ('docker', 'version', '--format', '{{.Server.Version}}'), requirements['docker.version']):
        raise RuntimeError(
            f"The correct docker version is not installed. Docker >= v{requirements['docker.version']} is needed."
        )

    if not correct_version_is_installed(
            ('docker-compose', 'version', '--short'), requirements['docker-compose.version']):
        raise RuntimeError(
            f"The correct docker-compose version is not installed. Docker-Compose >= v{requirements['docker-compose.version']} is needed."
        )

    if not correct_version_is_installed(
            ('openssl', 'version'), requirements['openssl.version']):
        raise RuntimeError(
            f"The correct openssl version is not installed. OpenSSL >= v{requirements['openssl.version']} is needed."
        )

    if not correct_version_is_installed(
            ('git', 'version'), requirements['git.version']):
        raise RuntimeError(
            f"The correct git version is not installed. Git >= v{requirements['git.version']} is needed."
        )


def parser() -> ArgumentParser:
    """
    Create an argument parser for all the script's arguments.

    Returns:
        The customized ArgumentParser object.
    """
    parser_: ArgumentParser = ArgumentParser(
        prog='laravel',
        description='A script to scaffold laravel projects.',
        allow_abbrev=False
    )

    setup: ArgumentParser = parser_.add_subparsers(
        title='Action',
        description='The action to take.',
        dest='action',
        required=True
    ).add_parser(
        'setup',
        description='Setup a new laravel project.',
        add_help=True,
        allow_abbrev=False
    )

    setup.add_argument(
        'project_name',
        help='The name of the laravel project to scaffold.'
    )
    setup.add_argument(
        '--domain',
        default='application.local',
        help='The domain name where the project will be hosted.'
    )
    setup.add_argument(
        '--with',
        nargs='*',
        choices=('everything', 'horizon', 'sanctum', 'scout', 'socialite', 'telescope'),
        help='Additional packages to install.'
    )
    setup.add_argument(
        '--development',
        action='store_true',
        help='Install the development version of laravel.'
    )

    return parser_


def validate_script_arguments(arguments: Namespace) -> None:
    if not is_pascal_case(arguments.project_name):
        raise RuntimeError(f"The project name: '{arguments.project_name}' is not pascal-cased.")

    if directory_exists(arguments.project_name):
        raise RuntimeError(
            f"The directory: '{arguments.project_name}' already exists in the current working directory.")

    if not domain_is_valid(arguments.domain):
        raise RuntimeError(f"The domain: '{arguments.domain}' is invalid.")


def scaffold_project_directory_structure(directory_structure: Mapping[str, ...]) -> None:
    if not directory_structure_is_valid(directory_structure):
        raise RuntimeError("The project's provided directory structure is invalid.")

    create_directory_structure(directory_structure)
