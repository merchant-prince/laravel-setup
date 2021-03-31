"""
This module contains code extracted from other scripts (mostly main.py)
"""

from argparse import ArgumentParser, Namespace
from os import getuid, getgid
from pathlib import Path
from shutil import copyfile
from string import Template
from typing import Any, Mapping, Union

from modules.scaffolding import directory_structure_is_valid, create_directory_structure, \
    generate_self_signed_tls_certificate
from modules.utilities import cd, template_path
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
        choices=('sanctum', 'scout', 'socialite'),
        help='Additional packages to install.'
    )
    setup_subparser.add_argument(
        '--development',
        action='store_true',
        help='Install the development version of laravel.'
    )

    return main_parser


def validate_script_arguments(arguments: Namespace) -> None:
    if not is_pascal_case(arguments.project_name):
        raise RuntimeError(f"The project name: '{arguments.project_name}' is not pascal-cased.")

    if directory_exists(arguments.project_name):
        raise RuntimeError(
            f"The directory: '{arguments.project_name}' already exists in the current working directory.")

    if not domain_is_valid(arguments.domain):
        raise RuntimeError(f"The domain: '{arguments.domain}' is invalid.")


def scaffold_project_directory_structure(directory_structure: Mapping[str, Any]) -> None:
    if not directory_structure_is_valid(directory_structure):
        raise RuntimeError("The project's provided directory structure is invalid.")

    create_directory_structure(directory_structure)


def generate_project_configuration_files(configuration: Mapping[str, Union[str, int]]) -> None:
    with cd(configuration['project.name']):
        with cd('configuration/nginx/ssl'):
            generate_self_signed_tls_certificate(
                certificate_name=configuration['services.nginx.ssl.certificate.name'],
                key_name=configuration['services.nginx.ssl.key.name'],
                domain=configuration['project.domain']
            )

        with open('docker-compose.yml', 'w') as file, open(f"{template_path('docker-compose.yml')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration['project.name'],
                    'USER_ID': getuid(),
                    'GROUP_ID': getgid(),
                    'POSTGRES_DB': configuration['services.postgres.database'],
                    'POSTGRES_USER': configuration['services.postgres.username'],
                    'POSTGRES_PASSWORD': configuration['services.postgres.password'],
                    'ADMINER_PORT': configuration['services.adminer.port'],
                    'MAILHOG_PORT': configuration['services.mailhog.port'],
                })
            )

        with open('run', 'w') as file, open(f"{template_path('run')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration['project.name'],
                    'NODE_IMAGE_TAG': configuration['miscellaneous.node.image.tag'],
                })
            )

        Path('run').chmod(0o755)

        copyfile(template_path('.gitignore'), f'{Path.cwd()}/.gitignore')

        with open('README.md', 'w') as file, open(f"{template_path('README.md')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration['project.name'],
                    'PROJECT_DOMAIN': configuration['project.domain'],
                    'SSL_KEY_NAME': configuration['services.nginx.ssl.key.name'],
                    'SSL_CERTIFICATE_NAME': configuration['services.nginx.ssl.certificate.name'],
                    'ADMINER_PORT': configuration['services.adminer.port'],
                    'MAILHOG_PORT': configuration['services.mailhog.port'],
                })
            )

        with cd('configuration'):
            with cd('nginx/conf.d'):
                with open('default.conf', 'w') as file, \
                        open(f"{template_path('configuration/nginx/conf.d/default.conf')}") as template:
                    file.write(
                        Template(template.read()).substitute({
                            'PROJECT_DOMAIN': configuration['project.domain'],
                            'SSL_KEY_NAME': configuration['services.nginx.ssl.key.name'],
                            'SSL_CERTIFICATE_NAME': configuration['services.nginx.ssl.certificate.name'],
                        })
                    )

                with open('utils.conf', 'w') as file, \
                        open(f"{template_path('configuration/nginx/conf.d/utils.conf')}") as template:
                    file.write(
                        Template(template.read()).substitute({
                            'PROJECT_DOMAIN': configuration['project.domain'],
                            'ADMINER_PORT': configuration['services.adminer.port'],
                            'MAILHOG_PORT': configuration['services.mailhog.port'],
                        })
                    )

            with cd('supervisor/conf.d'):
                copyfile(
                    template_path('configuration/supervisor/conf.d/supervisord.conf'),
                    f'{Path.cwd()}/supervisord.conf'
                )

        with cd('docker-compose/services/php'):
            copyfile(template_path('docker-compose/services/php/Dockerfile'), f'{Path.cwd()}/Dockerfile')
