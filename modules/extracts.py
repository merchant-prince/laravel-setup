from argparse import ArgumentParser


def parser() -> ArgumentParser:
    """
    Create an argument parser for all the arguments passed to the script.

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
        '--packages',
        nargs='*',
        choices=('all', 'horizon', 'sanctum', 'scout', 'socialite', 'telescope'),
        help='Additional packages to install.'
    )
    setup.add_argument(
        '--development',
        action='store_true',
        help='Install the development version of laravel.'
    )

    return parser_
