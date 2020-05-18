"""
A script to automate the installation of Laravel projects on Docker.
"""

import logging
import os
import re
from argparse import ArgumentParser
from collections import namedtuple
from collections.abc import Mapping
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace


@contextmanager
def cd(destination):
    """
    A context manager to change directory. Mimics unix's cd.

    Args:
        destination (str): The directory to cd into.
    """

    cwd = os.getcwd()

    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)


class Validation:
    """
    This class takes care of the validation needs of the application.

    Every validation rule is defined as a static method.
    """

    @staticmethod
    def is_pascal_case(string: str) -> bool:
        pascal_case_regex = re.compile(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$')

        return pascal_case_regex.match(string) is not None

    @staticmethod
    def domain_is_valid(domain: str) -> bool:
        domain_regex = re.compile(
            r'^'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'  # domain
            r'(?:/?|[/?]\S+)'  # path
            r'$',
            re.IGNORECASE
        )

        return domain_regex.match(domain) is not None

    @staticmethod
    def directory_exists(name: str) -> bool:
        return Path(f'{Path.cwd()}/{name}').is_dir()


class Skeleton:
    """
    A class to create a directory structure in the current directory.
    """

    @staticmethod
    def create(structure: Mapping) -> None:
        """
        Validate and create directories based on the provided structure.

        Args:
            structure (dict):
                The directory structure to create in the current directory.
                This is generally a dictionary of dictionaries.
                The empty dictionaries represent directories to be created.

                e.g.: { 'one': {
                            'eleven': {},
                            'twelve': {
                                'inner-directory': {}
                            }
                        }
                    }
        """

        Skeleton._validate(structure)
        Skeleton._create(structure)

    @staticmethod
    def _create(structure: Mapping) -> None:
        """
        Create directories according to the structure provided.

        Args:
            structure (Mapping): The directory structure to create in the current directory.
        """

        for name, structure in structure.items():
            if isinstance(structure, Mapping):
                os.mkdir(name)

                with cd(name):
                    Skeleton._create(structure)

    @staticmethod
    def _validate(structure: Mapping) -> None:
        """
        Validate the directory structure provided.

        Args:
            structure (Mapping): The directory structure to validate.

        Raises:
            ValueError: If the given structure is invalid.
        """

        if not isinstance(structure, Mapping):
            raise ValueError('The directory structure provided is ill-formed.')

        for name, structure in structure.items():
            if isinstance(structure, Mapping):
                Skeleton._validate(structure)
            else:
                raise ValueError('The directory structure provided is ill-formed.')


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s]: %(msg)s',
        level=logging.INFO
    )

    parser = namedtuple('Parser', ('main', 'subparser', 'subparsers'))(
        main := ArgumentParser(
            prog='laravel',
            description='A script to scaffold Laravel projects.',
            epilog='Build something awesome!',
            allow_abbrev=False
        ),
        main.add_subparsers(
            title='Action',
            description='The action to take.',
            dest='action',
            required=True
        ),
        SimpleNamespace()
    )

    # setup
    parser.subparsers.setup = parser.subparser.add_parser(
        'setup',
        description='Setup a new Laravel project.',
        epilog='Do it!',
        add_help=True,
        allow_abbrev=False
    )
    parser.subparsers.setup.add_argument(
        'project_name',
        help='The name of the project to scaffold.'
    )
    parser.subparsers.setup.add_argument(
        '--domain',
        default='application.local',
        help='The domain name where the project will be hosted.'
    )

    # parse arguments
    arguments = parser.main.parse_args()

    if arguments.action == 'setup':
        # validation
        if not Validation.is_pascal_case(arguments.project_name):
            raise RuntimeError(f'The project name: {arguments.project_name} is not pascal-cased.')

        if Validation.directory_exists(arguments.project_name):
            raise RuntimeError(f'The directory {arguments.project_name} already exists in {Path.cwd()}.')

        if not Validation.domain_is_valid(arguments.domain):
            raise RuntimeError(f'The domain: {arguments.domain} is invalid.')

        # configuration
        configuration = {
            # project-level configuration values.
            'project': {
                'name': arguments.project_name,
                'domain': arguments.domain
            }
        }

        # directory structure
        Skeleton.create({
            configuration['project']['name']: {
                'configuration': {
                    'nginx': {
                        'conf.d': {},
                        'ssl': {}
                    },
                    'php': {},
                    'postgresql': {},
                    'redis': {},
                    'adminer': {},
                    'selenium': {},
                    'firefox': {}
                },
                'docker-compose': {
                    'services': {
                        'nginx': {},
                        'php': {},
                        'postgresql': {},
                        'redis': {},
                        'adminer': {},
                        'selenium': {},
                        'firefox': {}
                    }
                },
                'application': {}
            }
        })
