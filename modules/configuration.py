from argparse import Namespace, ArgumentParser
from typing import Callable, Union, List, Mapping

from modules.verification import is_pascal_case, directory_exists, domain_is_valid


def create_argument_parser() -> ArgumentParser:
    main_parser: ArgumentParser = ArgumentParser(
        prog='laravel',
        description='A script to scaffold laravel projects.',
        allow_abbrev=False
    )

    setup_subparser: ArgumentParser = main_parser.add_subparsers(
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

    setup_subparser.add_argument(
        'project_name',
        help='The name of the laravel project to scaffold.'
    )
    setup_subparser.add_argument(
        '--domain',
        default='application.local',
        help='The domain name where the project will be hosted.'
    )
    setup_subparser.add_argument(
        '--with',
        nargs='*',
        choices=('horizon', 'sanctum', 'scout', 'socialite', 'telescope'),
        help='Additional packages to install.'
    )

    return main_parser


def validated_script_arguments(script_arguments: Namespace) -> Mapping[str, Union[str, List]]:
    if not is_pascal_case(script_arguments.project_name):
        raise RuntimeError(f"The project name: '{script_arguments.project_name}' is not pascal-cased.")

    if directory_exists(script_arguments.project_name):
        raise RuntimeError(
            f"The directory: '{script_arguments.project_name}' already exists in the current working directory.")

    if not domain_is_valid(script_arguments.domain):
        raise RuntimeError(f"The domain: '{script_arguments.domain}' is invalid.")

    return {
        'project_name': script_arguments.project_name,
        'project_domain': script_arguments.domain,
        'project_modules': script_arguments.__getattribute__('with') or [],
    }


ConfigurationType = Union[str, int, List]
ConfigurationAccessorType = Callable[[str], ConfigurationType]


def create_configuration_accessor(project_name: str, project_domain: str,
                                  project_modules: List) -> ConfigurationAccessorType:
    configuration: Mapping[str, ConfigurationType] = {
        'project.name': project_name,
        'project.domain': project_domain,
        'project.modules': project_modules,

        'services.nginx.ssl.certificate.name': 'certificate.pem',
        'services.nginx.ssl.key.name': 'key.pem',

        'services.postgres.database': project_name.lower(),
        'services.postgres.username': 'username',
        'services.postgres.password': 'password',

        'services.adminer.port': 8080,
        'services.mailhog.port': 8025,

        'miscellaneous.node.image.tag': 'stretch',
    }

    def _accessor(key: str) -> ConfigurationType:
        nonlocal configuration

        return configuration[key]

    return _accessor
