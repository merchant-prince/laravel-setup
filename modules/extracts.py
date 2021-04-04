"""
This module contains code extracted from other scripts (mostly main.py)
"""

from os import getuid, getgid, getcwd
from pathlib import Path
from shutil import copyfile
from string import Template
from subprocess import run
from typing import Mapping

from modules.configuration import ConfigurationAccessorType
from modules.configuration import create_argument_parser, validated_script_arguments, create_configuration_accessor
from modules.generators import setup_directory_structure, generate_self_signed_tls_certificate
from modules.utilities import cd, template_path
from modules.verification import correct_version_is_installed


def preflight_checks() -> None:
    """
    Checks whether the correct version of the dependencies of the script are installed.
    """
    requirements: Mapping[str, str] = {
        'docker.version': '20.10.5',
        'docker-compose.version': '1.28.0',
        'openssl.version': '1.1.1',
        'git.version': '2.31.0',
    }

    if not correct_version_is_installed(
            ('docker', 'version', '--format', '{{.Server.Version}}'), requirements['docker.version']):
        raise RuntimeError(
            'The correct docker version is not installed. '
            f"Docker >= v{requirements['docker.version']} is needed."
        )

    if not correct_version_is_installed(
            ('docker-compose', 'version', '--short'), requirements['docker-compose.version']):
        raise RuntimeError(
            'The correct docker-compose version is not installed. '
            f"Docker-Compose >= v{requirements['docker-compose.version']} is needed."
        )

    if not correct_version_is_installed(
            ('openssl', 'version'), requirements['openssl.version']):
        raise RuntimeError(
            'The correct openssl version is not installed. '
            f"OpenSSL >= v{requirements['openssl.version']} is needed."
        )

    if not correct_version_is_installed(
            ('git', 'version'), requirements['git.version']):
        raise RuntimeError(
            f"The correct git version is not installed. Git >= v{requirements['git.version']} is needed."
        )


def configure() -> ConfigurationAccessorType:
    """
    Instantiates a configuration accessor for the project.
    """
    return create_configuration_accessor(
        **validated_script_arguments(
            create_argument_parser().parse_args()
        )
    )


def ignition(configuration: ConfigurationAccessorType) -> None:
    setup_directory_structure(configuration('project.name'))


def main_engine_start(configuration: ConfigurationAccessorType) -> None:
    with cd(configuration('project.name')):
        with cd('configuration/nginx/ssl'):
            generate_self_signed_tls_certificate(
                domain=configuration('project.domain'),
                certificate_name=configuration('services.nginx.ssl.certificate.name'),
                key_name=configuration('services.nginx.ssl.key.name')
            )

        with open('docker-compose.yml', 'w') as file, open(f"{template_path('docker-compose.yml')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration('project.name'),
                    'USER_ID': getuid(),
                    'GROUP_ID': getgid(),
                    'POSTGRES_DB': configuration('services.postgres.database'),
                    'POSTGRES_USER': configuration('services.postgres.username'),
                    'POSTGRES_PASSWORD': configuration('services.postgres.password'),
                    'ADMINER_PORT': configuration('services.adminer.port'),
                    'MAILHOG_PORT': configuration('services.mailhog.port'),
                })
            )

        with open('run', 'w') as file, open(f"{template_path('run')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration('project.name'),
                    'NODE_IMAGE_TAG': configuration('miscellaneous.node.image.tag'),
                })
            )

        Path('run').chmod(0o755)

        copyfile(template_path('.gitignore'), f'{Path.cwd()}/.gitignore')

        with open('README.md', 'w') as file, open(f"{template_path('README.md')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration('project.name'),
                    'PROJECT_DOMAIN': configuration('project.domain'),
                    'SSL_KEY_NAME': configuration('services.nginx.ssl.key.name'),
                    'SSL_CERTIFICATE_NAME': configuration('services.nginx.ssl.certificate.name'),
                    'ADMINER_PORT': configuration('services.adminer.port'),
                    'MAILHOG_PORT': configuration('services.mailhog.port'),
                })
            )

        with cd('configuration'):
            with cd('nginx/conf.d'):
                with open('default.conf', 'w') as file, \
                        open(f"{template_path('configuration/nginx/conf.d/default.conf')}") as template:
                    file.write(
                        Template(template.read()).substitute({
                            'PROJECT_DOMAIN': configuration('project.domain'),
                            'SSL_KEY_NAME': configuration('services.nginx.ssl.key.name'),
                            'SSL_CERTIFICATE_NAME': configuration('services.nginx.ssl.certificate.name'),
                        })
                    )

                with open('utils.conf', 'w') as file, \
                        open(f"{template_path('configuration/nginx/conf.d/utils.conf')}") as template:
                    file.write(
                        Template(template.read()).substitute({
                            'PROJECT_DOMAIN': configuration('project.domain'),
                            'ADMINER_PORT': configuration('services.adminer.port'),
                            'MAILHOG_PORT': configuration('services.mailhog.port'),
                        })
                    )

            with cd('supervisor/conf.d'):
                copyfile(
                    template_path('configuration/supervisor/conf.d/supervisord.conf'),
                    f'{Path.cwd()}/supervisord.conf'
                )

        with cd('docker-compose/services/php'):
            copyfile(template_path('docker-compose/services/php/Dockerfile'), f'{Path.cwd()}/Dockerfile')


def countdown(configuration: ConfigurationAccessorType) -> None:
    with cd(f"{configuration('project.name')}/application/core"):
        run(
            (
                'docker', 'run',
                '--rm',
                '--interactive',
                '--tty',
                '--user',
                f'{getuid()}:{getgid()}',
                '--mount', f'type=bind,source={getcwd()},target=/application',
                '--workdir', '/application',
                'composer', 'create-project',
                '--prefer-dist',
                '--ignore-platform-reqs',
                'laravel/laravel', configuration('project.name'),
            ),
            check=True
        )


def takeoff(configuration: ConfigurationAccessorType) -> None:
    with cd(f"{configuration('project.name')}/application/core/{configuration('project.name')}"):
        run(('git', 'init'), check=True)
        run(('git', 'add', '*'), check=True)
        run(('git', 'commit', '--message', 'initial commit'), check=True)
        run(('git', 'checkout', '-b', 'development'), check=True)
