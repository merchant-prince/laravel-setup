"""
A script to automate the installation of Laravel projects on Docker.
"""

import re
import logging
from argparse import ArgumentParser
from collections import namedtuple
from types import SimpleNamespace


class Validation:
    @staticmethod
    def is_pascal_case(value: str) -> bool:
        pascal_case_regex = re.compile(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$')

        return pascal_case_regex.match(value) is not None

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

        if not Validation.domain_is_valid(arguments.domain):
            raise RuntimeError(f'The domain: {arguments.domain} is invalid.')
